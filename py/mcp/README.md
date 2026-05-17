# MCP Process Monitor Server

基于 Python FastMCP 的远程服务器进程监控工具，支持 HTTPS 加密和 AK/SK 签名认证。可通过 MCP 代理接入 Claude Code / VS Code / Cursor。

## 功能特性

- **进程内存排行**: Top N 进程内存占用（RSS）
- **进程 CPU 排行**: Top N 进程 CPU 占用（多核可超 100%）
- **HTTPS 传输加密**: 基于 CA 签名的 TLS 证书链
- **AK/SK 认证**: HMAC-SHA256 签名，防重放攻击，SK 加密存储于 SQLite
- **远程代理**: 零依赖代理脚本，Windows 客户端无需 `pip install` 即可接入

## 项目结构

```
py/mcp/
  server.py                        # 主服务器入口
  auth.py                          # 认证模块（签名、SQLite、Starlette 中间件）
  manage_keys.py                   # AK/SK 密钥管理 CLI
  client_example.py                # 客户端调用示例（MCP JSON-RPC）
  remote_proxy.py                  # 远程代理（零依赖版，推荐 Windows 使用）
  remote_proxy_requirements.py     # 远程代理（SDK 版，httpx 连接池）
  configs/
    base.json                      # 配置文件
  certs/
    ca.crt                         # CA 根证书（客户端需持有）
    ca.key                         # CA 私钥（仅签发用，勿分发）
    server.crt                     # 服务器证书
    server.key                     # 服务器私钥
  data/
    aksk.db                        # SQLite 数据库（自动创建）
  pyproject.toml                   # uv 项目配置
  requirements.txt                 # pip 兼容的依赖列表
```

## 快速开始

### 1. 环境准备

```bash
cd /code/CUTeMoL/exercise/py/mcp

# 方式一：uv（推荐）
uv sync

# 方式二：pip + venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. 生成证书

如已有证书可跳过。将 `<你的服务器IP>` 替换为实际 IP。

```bash
# 生成 CA 根证书
openssl genrsa -out certs/ca.key 4096
openssl req -x509 -new -nodes -key certs/ca.key -sha256 -days 3650 \
  -out certs/ca.crt \
  -subj "/C=CN/ST=Beijing/L=Beijing/O=MCP-CA/CN=MCP-Root-CA"

# 服务器证书配置
cat > /tmp/server.cnf << EOF
[req]
default_bits = 2048
prompt = no
default_md = sha256
distinguished_name = dn
req_extensions = req_ext

[dn]
C = CN
ST = Beijing
L = Beijing
O = MCP-Server
CN = mcp-server

[req_ext]
subjectAltName = @alt_names

[alt_names]
DNS.1 = localhost
IP.1 = 127.0.0.1
IP.2 = <你的服务器IP>
EOF

# 生成服务器证书并由 CA 签发
openssl genrsa -out certs/server.key 2048
openssl req -new -key certs/server.key -out /tmp/server.csr -config /tmp/server.cnf
openssl x509 -req -in /tmp/server.csr -CA certs/ca.crt -CAkey certs/ca.key \
  -CAcreateserial -out certs/server.crt -days 365 -sha256 \
  -extfile /tmp/server.cnf -extensions req_ext

# 验证证书链
openssl verify -CAfile certs/ca.crt certs/server.crt
```

### 3. 创建 AK/SK

```bash
python manage_keys.py create --description "admin key"
# 输出:
# Access Key: ak-xxxx...
# Secret Key: sk-xxxx...  ← 仅显示一次，务必保存
```

其他管理命令：

```bash
python manage_keys.py list                      # 列出所有密钥
python manage_keys.py disable <access_key>       # 禁用密钥
python manage_keys.py verify --ak <ak> --sk <sk> # 验证签名（自测用）
```

### 4. 启动服务端

```bash
uv run python server.py
# 监听 https://0.0.0.0:8443
```

配置项在 `configs/base.json`：

```json
{
  "server": { "host": "0.0.0.0", "port": 8443 },
  "sqlite": { "path": "data/aksk.db" },
  "ssl": {
    "cert_file": "certs/server.crt",
    "key_file": "certs/server.key",
    "ca_cert_file": "certs/ca.crt"
  },
  "auth": {
    "timestamp_tolerance_seconds": 300,
    "master_key": "自动生成，勿手动修改"
  }
}
```

## 远程代理（Claude Code 接入）

这是本项目的核心功能——在 Windows/Mac 客户端的 Claude Code 中直接调用远程 Linux 服务器的 MCP 工具。

### 架构

```
Windows Claude Code
    │ stdio JSON-RPC
    ▼
remote_proxy.py           ← 零依赖，装 Python 即可
    │ HTTPS + AK/SK 签名
    ▼
server.py (Linux)         ← 远程 MCP 服务器
```

### 零依赖版（推荐）

Windows 上只需安装 Python 3.10+，无需 `pip install` 任何包。

1. 复制文件到 Windows：
   - `remote_proxy.py`
   - `certs/ca.crt`（如需 SSL 验证）

2. 在 Claude Code 的 `mcp.json` 中配置：

```json
{
  "mcpServers": {
    "remote-monitor": {
      "command": "python",
      "args": [
        "C:/Users/xxx/remote_proxy.py",
        "--host", "172.26.72.248",
        "--port", "8443",
        "--ak", "ak-xxxxxxxx",
        "--sk", "sk-xxxxxxxx",
        "--ca-cert", "C:/Users/xxx/ca.crt"
      ]
    }
  }
}
```

3. 重启 Claude Code，即可在对话中调用 `get_top_memory_processes` 和 `get_top_cpu_processes`。

### SDK 版（有依赖）

需要 `pip install mcp httpx`，但使用官方 MCP SDK 和 httpx 连接池，连接效率更高。

```json
{
  "mcpServers": {
    "remote-monitor": {
      "command": "python",
      "args": [
        "C:/Users/xxx/remote_proxy_requirements.py",
        "--host", "172.26.72.248",
        "--port", "8443",
        "--ak", "ak-xxxxxxxx",
        "--sk", "sk-xxxxxxxx"
      ]
    }
  }
}
```

### 两个代理版本对比

| | `remote_proxy.py` | `remote_proxy_requirements.py` |
|---|---|---|
| 依赖 | 无（Python 标准库） | `mcp` + `httpx` |
| Windows 准备 | 复制文件即用 | `pip install mcp httpx` |
| HTTP 连接 | `urllib`，每请求新建连接 | `httpx.AsyncClient` 连接池 |
| MCP 协议 | 手动解析 stdin JSON-RPC | `mcp.server.Server` SDK |
| 适用场景 | 快速部署、临时使用 | 长期使用、高频调用 |

## MCP 工具接口

### get_top_memory_processes

查询进程内存占用排行（RSS 单位 B）。

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| limit | int | 10 | 返回前 N 个进程 |

返回字段：`pid` (int), `name` (str), `memory_bytes` (int)

### get_top_cpu_processes

查询进程 CPU 占用排行（每核 100%）。

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| limit | int | 10 | 返回前 N 个进程 |
| interval | float | 0.1 | CPU 采样间隔（秒） |

返回字段：`pid` (int), `name` (str), `cpu_percent` (float)

> **CPU 百分比说明**: 每个 CPU 核心独立计算 100%。例如在 4 核机器上，一个进程占满所有核心会显示 ~400%。

### 新增工具

在 `tools/` 目录下新建 `.py` 文件，按模块模式实现工具函数并加入 `_tools` 列表即可，`__init__.py` 会自动发现并注册：

```python
# tools/disk.py
import shutil


def get_disk_usage(path: str = "/") -> dict:
    """查询磁盘使用情况。"""
    usage = shutil.disk_usage(path)
    return {
        "path": path,
        "total_gb": round(usage.total / (1024**3), 1),
        "free_gb": round(usage.free / (1024**3), 1),
        "percent": round(usage.used / usage.total * 100, 1),
    }


_tools = [get_disk_usage]


def register_tools(mcp):
    for tool in _tools:
        mcp.tool()(tool)
```

重启后代理端自动同步新工具。

- 函数签名自动生成 `inputSchema`（参数类型 + 默认值）
- docstring 自动生成工具描述
- 同步函数用 `def`，FastMCP 自动放入线程池
- I/O 密集型（异步 DB、网络请求）用 `async def`

## 安全架构

### 传输加密

```
客户端 --[CA 验证服务器证书]--> TLS 1.2+ --> 服务器
```

- 服务器证书由私有 CA 签发，客户端通过信任 CA 证书来验证服务器身份
- CA 私钥 (`certs/ca.key`) 应妥善保管，仅用于签发证书
- 客户端需持有 CA 证书 (`certs/ca.crt`) 方可验证

### AK/SK 认证流程

```
客户端                                   服务器
  |                                        |
  |-- POST /mcp ------------------------>  |
  |   Headers:                             |
  |     X-AK: <access_key>                 |
  |     X-Timestamp: <unix_seconds>        |
  |     X-Signature: <hmac_sha256_hex>     |
  |   Body: JSON-RPC request               |
  |                                        |
  |              服务器端验证:               |
  |              1. 检查 |now - ts| < 300s  |
  |              2. 查 SQLite 获取 SK       |
  |              3. 重算 HMAC 对比签名       |
  |              4. 返回结果或 401           |
  |                                        |
  |<-- JSON-RPC response -----------------|
```

签名算法：

```
CanonicalString = HTTP_METHOD + "\n" + URL_PATH + "\n" + TIMESTAMP + "\n" + SHA256(BODY)
Signature = hex(HMAC-SHA256(SK, CanonicalString))
```

### SK 存储安全

- SK 使用 Fernet（AES-128-CBC + HMAC）加密后存入 SQLite
- 加密主密钥自动生成并存储在 `configs/base.json` 的 `auth.master_key` 中
- 生产环境建议将 `configs/base.json` 权限设为 600

### 防重放攻击

通过 `X-Timestamp` 时间戳校验（默认 ±300s 容差），超出窗口的请求自动拒绝。

## 配置说明

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| server.host | 监听地址 | 0.0.0.0 |
| server.port | 监听端口 | 8443 |
| sqlite.path | 数据库路径 | data/aksk.db |
| ssl.cert_file | 服务器证书 | certs/server.crt |
| ssl.key_file | 服务器私钥 | certs/server.key |
| ssl.ca_cert_file | CA 证书 | certs/ca.crt |
| auth.timestamp_tolerance_seconds | 时间戳容差 | 300 |
| auth.master_key | 加密主密钥 | 自动生成 |

## 部署建议

### 生产环境

```bash
# 1. 使用正规 CA 证书（Let's Encrypt 等），或至少使用内部 CA
# 2. 限制配置文件权限
chmod 600 configs/base.json
# 3. 使用专用用户运行
useradd -r mcp && chown -R mcp:mcp /code/CUTeMoL/exercise/py/mcp
sudo -u mcp python server.py
# 4. 配置防火墙（仅允许信任的 IP 访问 8443）
```
