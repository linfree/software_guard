# ============================================================
# Stage 1: 构建前端
# ============================================================
FROM node:20-alpine AS frontend-builder

WORKDIR /app/frontend

RUN npm install -g pnpm@latest

COPY frontend/package.json frontend/pnpm-lock.yaml ./

RUN pnpm install --frozen-lockfile --prod=false

COPY frontend/ ./

RUN pnpm build


# ============================================================
# Stage 2: 最终运行镜像
# ============================================================
FROM python:3.12-slim AS runtime

LABEL maintainer="Software Guard Team"
LABEL description="Software Guard - 企业级软件分发管理平台"
LABEL org.opencontainers.image.source="https://github.com/your-org/software_guard"

WORKDIR /app

# 仅安装运行时必需的系统依赖，不保留包管理器缓存
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       libpq5 \
       curl \
    && rm -rf /var/lib/apt/lists/* \
    && groupadd -r appuser && useradd -r -g appuser -d /app -s /sbin/nologin appuser

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

COPY backend/pyproject.toml ./
RUN uv pip install --system --no-cache -r pyproject.toml

COPY backend/ ./

COPY --from=frontend-builder /app/frontend/dist ./static

RUN mkdir -p storage && chown -R appuser:appuser /app

USER appuser

ENV STORAGE_PATH=storage \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
