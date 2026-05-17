"""
AK/SK 认证模块。

提供:
- 从 configs/base.json 加载配置
- 基于 SQLite 的 AK/SK 密钥存储（SK 使用 Fernet 加密）
- HMAC-SHA256 签名验证（类 AWS SigV4 协议）
- Starlette HTTP 中间件，带审计日志和请求体大小限制
"""
import hashlib
import hmac
import json
import logging
import os
import secrets
import sqlite3
import time
from pathlib import Path

from cryptography.fernet import Fernet
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════
# 配置加载
# ═══════════════════════════════════════════════════════════════════

def load_config(config_path: str = "configs/base.json") -> dict:
    """加载 JSON 配置文件，将相对路径转为绝对路径。"""
    project_root = Path(__file__).parent
    with open(project_root / config_path) as f:
        config = json.load(f)

    # 将相对路径转为绝对路径
    sqlite_path = config["sqlite"]["path"]
    if not os.path.isabs(sqlite_path):
        config["sqlite"]["path"] = str(project_root / sqlite_path)
    for key in ["cert_file", "key_file", "ca_cert_file"]:
        path = config["ssl"][key]
        if not os.path.isabs(path):
            config["ssl"][key] = str(project_root / path)

    return config


# ═══════════════════════════════════════════════════════════════════
# 主密钥管理（用于加密存储 SK）
# ═══════════════════════════════════════════════════════════════════

def get_master_key(config: dict) -> bytes:
    """获取或自动生成用于加密 SK 的 Fernet 主密钥。"""
    key_str = config.get("auth", {}).get("master_key", "")
    if key_str:
        return key_str.encode()

    # 未配置则自动生成，写回配置文件
    new_key = Fernet.generate_key()
    config_path = Path(__file__).parent / "configs" / "base.json"
    with open(config_path) as f:
        cfg = json.load(f)
    cfg.setdefault("auth", {})["master_key"] = new_key.decode()
    with open(config_path, "w") as f:
        json.dump(cfg, f, indent=2)
    config["auth"]["master_key"] = new_key.decode()
    logger.info("已生成主密钥并保存到 configs/base.json")
    return new_key


def encrypt_sk(sk: str, master_key: bytes) -> str:
    """使用 Fernet 加密 Secret Key。"""
    return Fernet(master_key).encrypt(sk.encode()).decode()


def decrypt_sk(encrypted: str, master_key: bytes) -> str:
    """使用 Fernet 解密 Secret Key。"""
    return Fernet(master_key).decrypt(encrypted.encode()).decode()


# ═══════════════════════════════════════════════════════════════════
# SQLite 操作
# ═══════════════════════════════════════════════════════════════════

def get_db_connection(db_path: str) -> sqlite3.Connection:
    """获取 SQLite 数据库连接（使用 Row 工厂）。"""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(conn: sqlite3.Connection) -> None:
    """初始化数据库表结构（如不存在则创建）。"""
    conn.execute("""
        CREATE TABLE IF NOT EXISTS api_keys (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            access_key TEXT UNIQUE NOT NULL,
            secret_key_encrypted TEXT NOT NULL,
            description TEXT DEFAULT '',
            enabled INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()


def generate_access_key() -> str:
    """生成 Access Key（ak- 前缀 + 32 位十六进制）。"""
    return "ak-" + secrets.token_hex(16)


def generate_secret_key() -> str:
    """生成 Secret Key（sk- 前缀 + 64 位十六进制）。"""
    return "sk-" + secrets.token_hex(32)


def create_api_key(conn: sqlite3.Connection, master_key: bytes, description: str = "") -> tuple[str, str]:
    """创建一对新的 AK/SK。返回 (access_key, raw_secret_key)。"""
    ak = generate_access_key()
    sk = generate_secret_key()
    encrypted_sk = encrypt_sk(sk, master_key)
    conn.execute(
        "INSERT INTO api_keys (access_key, secret_key_encrypted, description) VALUES (?, ?, ?)",
        (ak, encrypted_sk, description)
    )
    conn.commit()
    return ak, sk


def list_api_keys(conn: sqlite3.Connection) -> list[dict]:
    """列出所有 API 密钥（不包含加密的 SK）。"""
    rows = conn.execute(
        "SELECT id, access_key, description, enabled, created_at FROM api_keys ORDER BY id"
    ).fetchall()
    return [dict(r) for r in rows]


def disable_api_key(conn: sqlite3.Connection, access_key: str) -> bool:
    """禁用指定的 API 密钥。返回是否成功。"""
    cursor = conn.execute("UPDATE api_keys SET enabled = 0 WHERE access_key = ?", (access_key,))
    conn.commit()
    return cursor.rowcount > 0


def get_secret_key(conn: sqlite3.Connection, master_key: bytes, access_key: str) -> str | None:
    """根据 AK 查找并解密 SK。未找到或已禁用返回 None。"""
    row = conn.execute(
        "SELECT secret_key_encrypted FROM api_keys WHERE access_key = ? AND enabled = 1",
        (access_key,)
    ).fetchone()
    if row is None:
        return None
    return decrypt_sk(row["secret_key_encrypted"], master_key)


# ═══════════════════════════════════════════════════════════════════
# HMAC 签名验证
# ═══════════════════════════════════════════════════════════════════

def compute_signature(method: str, path: str, timestamp: str, body: bytes, secret_key: str) -> str:
    """对规范请求计算 HMAC-SHA256 签名。

    规范字符串: HTTP方法 + 换行 + URL路径 + 换行 + 时间戳 + 换行 + SHA256(请求体)
    """
    body_hash = hashlib.sha256(body).hexdigest()
    canonical = f"{method}\n{path}\n{timestamp}\n{body_hash}"
    return hmac.new(secret_key.encode(), canonical.encode(), hashlib.sha256).hexdigest()


def verify_signature(
    conn: sqlite3.Connection,
    master_key: bytes,
    access_key: str,
    signature: str,
    timestamp: str,
    method: str,
    path: str,
    body: bytes,
    tolerance: int = 300,
) -> tuple[bool, str]:
    """验证 AK/SK HMAC 签名。返回 (是否有效, 错误信息)。"""
    # 1. 检查时间戳新鲜度（防止重放攻击）
    try:
        ts = int(timestamp)
    except ValueError:
        return False, "Invalid timestamp format"

    now = int(time.time())
    if abs(now - ts) > tolerance:
        return False, "Timestamp expired"

    # 2. 查找 Secret Key
    sk = get_secret_key(conn, master_key, access_key)
    if sk is None:
        return False, "Invalid or disabled access key"

    # 3. 重新计算 HMAC 并使用恒定时间比较（防止时序攻击）
    expected = compute_signature(method, path, timestamp, body, sk)
    if not hmac.compare_digest(expected, signature):
        return False, "Signature mismatch"

    return True, ""


# ═══════════════════════════════════════════════════════════════════
# Starlette HTTP 中间件
# ═══════════════════════════════════════════════════════════════════

# 默认请求体大小限制: 1 MB
DEFAULT_MAX_BODY_SIZE = 1_048_576


class AkSkAuthMiddleware(BaseHTTPMiddleware):
    """基于 AK/SK HMAC 签名的认证中间件，带审计日志和请求体大小限制。

    所有 /mcp 请求必须携带 X-AK、X-Timestamp、X-Signature 头。
    /health 端点无需认证。
    """

    def __init__(self, app, db_path: str, master_key: bytes, tolerance: int = 300,
                 max_body_size: int = DEFAULT_MAX_BODY_SIZE):
        super().__init__(app)
        self.db_path = db_path
        self.master_key = master_key
        self.tolerance = tolerance
        self.max_body_size = max_body_size

    async def dispatch(self, request: Request, call_next):
        # /health 端点无需认证
        if request.url.path.rstrip("/") == "/health":
            return await call_next(request)

        # 获取客户端 IP 用于审计日志
        client_ip = request.client.host if request.client else "unknown"

        # 读取请求体，同时检查大小限制
        body = await request.body()
        if len(body) > self.max_body_size:
            logger.warning(
                f"请求体过大: {len(body)} bytes 来自 {client_ip} "
                f"(限制={self.max_body_size})"
            )
            return JSONResponse(
                {"error": f"Request body too large (max {self.max_body_size} bytes)"},
                status_code=413,
            )

        # 提取认证头
        ak = request.headers.get("X-AK", "")
        timestamp = request.headers.get("X-Timestamp", "")
        signature = request.headers.get("X-Signature", "")

        if not ak or not timestamp or not signature:
            logger.warning(
                f"认证失败: 缺少认证头 来自 {client_ip}"
            )
            return JSONResponse(
                {"error": "Missing authentication headers (X-AK, X-Timestamp, X-Signature)"},
                status_code=401,
            )

        # 验证签名
        conn = get_db_connection(self.db_path)
        try:
            valid, err_msg = verify_signature(
                conn, self.master_key, ak, signature, timestamp,
                request.method, request.url.path, body, self.tolerance
            )
        finally:
            conn.close()

        if not valid:
            logger.warning(
                f"认证失败: AK={ak[:12]}... 来自 {client_ip} "
                f"原因=\"{err_msg}\" {request.method} {request.url.path}"
            )
            return JSONResponse({"error": err_msg}, status_code=401)

        logger.info(
            f"认证通过: AK={ak[:12]}... 来自 {client_ip} "
            f"{request.method} {request.url.path}"
        )

        return await call_next(request)
