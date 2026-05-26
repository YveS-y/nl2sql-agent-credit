#!/bin/bash
set -e

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
FRONTEND_DIR="$PROJECT_DIR/data-agent-fronted/data-agent-fronted"

# 检查端口是否已被占用
check_port() {
    lsof -ti :$1 > /dev/null 2>&1
}

echo "==> 启动基础设施..."
docker compose -f "$PROJECT_DIR/docker-compose.yml" up -d

echo "==> 启动 Embedding 服务..."
if check_port 8081; then
    echo "    端口 8081 已占用，跳过"
else
    osascript -e "tell application \"Terminal\" to do script \"cd $PROJECT_DIR && uv run uvicorn docker.embedding.server:app --port 8081\""
fi

echo "==> 启动后端..."
if check_port 8000; then
    echo "    端口 8000 已占用，跳过"
else
    osascript -e "tell application \"Terminal\" to do script \"cd $PROJECT_DIR && uv run uvicorn main:app --host 0.0.0.0 --port 8000 --reload\""
fi

echo "==> 启动前端..."
if check_port 5173; then
    echo "    端口 5173 已占用，跳过"
else
    osascript -e "tell application \"Terminal\" to do script \"cd $FRONTEND_DIR && npm run dev\""
fi

echo ""
echo "所有服务启动中，稍后访问 http://localhost:5173"
