#!/bin/bash
# 只停止 Docker 基础设施（MySQL、Qdrant、ES）
PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "==> 停止基础设施..."
docker compose -f "$PROJECT_DIR/docker-compose.yml" down
