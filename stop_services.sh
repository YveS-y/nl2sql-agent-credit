#!/bin/bash
# 只停止前端、后端、Embedding，保留 Docker 基础设施

echo "==> 停止前端 (5173)..."
lsof -ti :5173 | xargs kill -9 2>/dev/null && echo "    前端已停止" || echo "    前端未运行"

echo "==> 停止后端 (8000)..."
lsof -ti :8000 | xargs kill -9 2>/dev/null && echo "    后端已停止" || echo "    后端未运行"

echo "==> 停止 Embedding (8081)..."
lsof -ti :8081 | xargs kill -9 2>/dev/null && echo "    Embedding 已停止" || echo "    Embedding 未运行"
