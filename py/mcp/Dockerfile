FROM ghcr.io/astral-sh/uv:python3.13-bookworm

WORKDIR /app

# 先复制依赖描述文件，利用 Docker 层缓存
COPY pyproject.toml requirements.txt ./

# 设置超时 600 秒、镜像源、重试 3 次
ENV UV_HTTP_TIMEOUT=600
ENV UV_RETRIES=3
# ENV UV_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple

# 安装生产依赖（fastmcp 会自动拉入 uvicorn）
RUN uv sync --no-dev 

# 复制应用代码
COPY *.py ./
COPY tools/ tools/
COPY configs/ configs/
COPY certs/ certs/
# COPY data/ data/

# 数据目录（SQLite 持久化，挂载 volume）
RUN mkdir -p data

EXPOSE 8443

ENTRYPOINT ["uv", "run", "--no-sync", "python", "server.py"]

# docker build -t mcp_tools_image:v0.1 -f Dockerfile .