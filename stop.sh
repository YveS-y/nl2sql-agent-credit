#!/bin/bash
PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "==> 停止前端 (5173)..."
lsof -ti :5173 | xargs kill -9 2>/dev/null && echo "    前端已停止" || echo "    前端未运行"

echo "==> 停止后端 (8000)..."
lsof -ti :8000 | xargs kill -9 2>/dev/null && echo "    后端已停止" || echo "    后端未运行"

echo "==> 停止 Embedding (8081)..."
lsof -ti :8081 | xargs kill -9 2>/dev/null && echo "    Embedding 已停止" || echo "    Embedding 未运行"

echo "==> 停止基础设施..."
docker compose -f "$PROJECT_DIR/docker-compose.yml" down
