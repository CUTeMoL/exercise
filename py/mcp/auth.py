"""
AK/SK Authentication module for MCP server.

Provides:
- Configuration loading from configs/base.json
- SQLite-backed AK/SK key storage (SK encrypted at rest with Fernet)
- HMAC-SHA256 signature verification (AWS SigV4-inspired protocol)
- ASGI middleware for request-level authentication
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

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════
# Configuration
# ═══════════════════════════════════════════════════════════════════

def load_config(config_path: str = "configs/base.json") -> dict:
    """Load configuration from JSON file, resolving relative paths to absolute."""
    project_root = Path(__file__).parent
    with open(project_root / config_path) as f:
        config = json.load(f)

    # Resolve relative paths
    sqlite_path = config["sqlite"]["path"]
    if not os.path.isabs(sqlite_path):
        config["sqlite"]["path"] = str(project_root / sqlite_path)
    for key in ["cert_file", "key_file", "ca_cert_file"]:
        path = config["ssl"][key]
        if not os.path.isabs(path):
            config["ssl"][key] = str(project_root / path)

    return config


# ═══════════════════════════════════════════════════════════════════
# Master Key Management (for SK encryption at rest)
# ═══════════════════════════════════════════════════════════════════

def get_master_key(config: dict) -> bytes:
    """Get or auto-generate the Fernet master key for encrypting SKs."""
    key_str = config.get("auth", {}).get("master_key", "")
    if key_str:
        return key_str.encode()

    # Auto-generate and persist back to config
    new_key = Fernet.generate_key()
    config_path = Path(__file__).parent / "configs" / "base.json"
    with open(config_path) as f:
        cfg = json.load(f)
    cfg.setdefault("auth", {})["master_key"] = new_key.decode()
    with open(config_path, "w") as f:
        json.dump(cfg, f, indent=2)
    config["auth"]["master_key"] = new_key.decode()
    logger.info("Generated new master key and saved to configs/base.json")
    return new_key


def encrypt_sk(sk: str, master_key: bytes) -> str:
    """Encrypt a secret key with Fernet."""
    return Fernet(master_key).encrypt(sk.encode()).decode()


def decrypt_sk(encrypted: str, master_key: bytes) -> str:
    """Decrypt a secret key with Fernet."""
    return Fernet(master_key).decrypt(encrypted.encode()).decode()


# ═══════════════════════════════════════════════════════════════════
# SQLite Operations
# ═══════════════════════════════════════════════════════════════════

def get_db_connection(db_path: str) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(conn: sqlite3.Connection) -> None:
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
    return "ak-" + secrets.token_hex(16)


def generate_secret_key() -> str:
    return "sk-" + secrets.token_hex(32)


def create_api_key(conn: sqlite3.Connection, master_key: bytes, description: str = "") -> tuple[str, str]:
    """Create a new AK/SK pair. Returns (access_key, raw_secret_key)."""
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
    rows = conn.execute(
        "SELECT id, access_key, description, enabled, created_at FROM api_keys ORDER BY id"
    ).fetchall()
    return [dict(r) for r in rows]


def disable_api_key(conn: sqlite3.Connection, access_key: str) -> bool:
    cursor = conn.execute("UPDATE api_keys SET enabled = 0 WHERE access_key = ?", (access_key,))
    conn.commit()
    return cursor.rowcount > 0


def get_secret_key(conn: sqlite3.Connection, master_key: bytes, access_key: str) -> str | None:
    """Retrieve and decrypt SK for a given AK. Returns None if not found or disabled."""
    row = conn.execute(
        "SELECT secret_key_encrypted FROM api_keys WHERE access_key = ? AND enabled = 1",
        (access_key,)
    ).fetchone()
    if row is None:
        return None
    return decrypt_sk(row["secret_key_encrypted"], master_key)


# ═══════════════════════════════════════════════════════════════════
# HMAC Signature Verification
# ═══════════════════════════════════════════════════════════════════

def compute_signature(method: str, path: str, timestamp: str, body: bytes, secret_key: str) -> str:
    """Compute HMAC-SHA256 signature over the canonical request."""
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
    """Verify an AK/SK HMAC signature. Returns (is_valid, error_message)."""
    # 1. Validate timestamp freshness (replay protection)
    try:
        ts = int(timestamp)
    except ValueError:
        return False, "Invalid timestamp format"

    now = int(time.time())
    if abs(now - ts) > tolerance:
        return False, "Timestamp expired"

    # 2. Look up secret key
    sk = get_secret_key(conn, master_key, access_key)
    if sk is None:
        return False, "Invalid or disabled access key"

    # 3. Recompute HMAC and compare (constant-time)
    expected = compute_signature(method, path, timestamp, body, sk)
    if not hmac.compare_digest(expected, signature):
        return False, "Signature mismatch"

    return True, ""


# ═══════════════════════════════════════════════════════════════════
# Starlette HTTP Middleware
# ═══════════════════════════════════════════════════════════════════

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse


class AkSkAuthMiddleware(BaseHTTPMiddleware):
    """Starlette HTTP middleware for AK/SK HMAC authentication."""

    def __init__(self, app, db_path: str, master_key: bytes, tolerance: int = 300):
        super().__init__(app)
        self.db_path = db_path
        self.master_key = master_key
        self.tolerance = tolerance

    async def dispatch(self, request: Request, call_next):
        # Allow unauthenticated access to /health
        if request.url.path.rstrip("/") == "/health":
            return await call_next(request)

        # Read body once (Starlette handles this efficiently)
        body = await request.body()

        # Extract auth headers
        ak = request.headers.get("X-AK", "")
        timestamp = request.headers.get("X-Timestamp", "")
        signature = request.headers.get("X-Signature", "")

        if not ak or not timestamp or not signature:
            return JSONResponse(
                {"error": "Missing authentication headers (X-AK, X-Timestamp, X-Signature)"},
                status_code=401,
            )

        # Verify signature
        conn = get_db_connection(self.db_path)
        try:
            valid, err_msg = verify_signature(
                conn, self.master_key, ak, signature, timestamp,
                request.method, request.url.path, body, self.tolerance
            )
        finally:
            conn.close()

        if not valid:
            return JSONResponse({"error": err_msg}, status_code=401)

        return await call_next(request)
