# Data-Agent Docker 部署指南

## 📋 环境要求

- Docker >= 20.0
- Docker Compose >= 2.0
- 内存 >= 4GB（Elasticsearch 需要较多内存）

## 🚀 快速启动

### 1. 配置环境变量

```bash
cd data-agent
cp .env.example .env
# 编辑 .env 文件，填入你的 LLM API Key
```

### 2. 启动基础服务

```bash
# 启动 MySQL、Qdrant、Elasticsearch
docker-compose up -d mysql qdrant elasticsearch

# 等待服务启动（约 30 秒）
docker-compose ps
```

### 3. 初始化元数据

MySQL 会自动执行 `docker/mysql/init/01_create_databases.sql` 创建表结构和示例数据。

### 4. 启动 Data-Agent 应用

```bash
# 构建并启动应用
docker-compose up --build -d data-agent

# 查看日志
docker-compose logs -f data-agent
```

### 5. 验证部署

```bash
# 检查所有服务状态
docker-compose ps

# 测试 API 是否可用
curl http://localhost:8000/health

# 查看 API 文档
open http://localhost:8000/docs
```

## 🛠️ 常用命令

```bash
# 查看所有服务日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs -f data-agent

# 重启服务
docker-compose restart data-agent

# 停止所有服务
docker-compose down

# 停止并删除数据卷（谨慎使用）
docker-compose down -v

# 进入容器调试
docker-compose exec data-agent bash
docker-compose exec mysql mysql -u atguigu -p
```

## 📁 目录结构

```
data-agent/
├── docker-compose.yml          # Docker 编排配置
├── Dockerfile                  # 应用镜像构建
├── .env.example                # 环境变量模板
├── docker/
│   ├── mysql/
│   │   └── init/               # MySQL 初始化脚本
│   └── embedding/              # Embedding 服务（可选）
├── conf/
│   ├── app_config.yaml         # 应用配置
│   └── meta_config.yaml        # 元数据配置
└── README-Docker.md            # 本文件
```

## 🔧 配置说明

### 数据库连接

Docker 环境中，应用通过服务名连接：
- MySQL: `mysql:3306`
- Qdrant: `qdrant:6333`
- Elasticsearch: `elasticsearch:9200`

### 端口映射

| 服务 | 容器端口 | 主机端口 | 说明 |
|------|----------|----------|------|
| Data-Agent | 8000 | 8000 | API 服务 |
| MySQL | 3306 | 3306 | 数据库 |
| Qdrant | 6333 | 6333 | 向量数据库 |
| Elasticsearch | 9200 | 9200 | 全文检索 |

## 📝 数据持久化

数据通过 Docker Volumes 持久化：
- `mysql_data`: MySQL 数据
- `qdrant_data`: Qdrant 向量数据
- `es_data`: Elasticsearch 数据

## 🐛 故障排查

### 1. MySQL 连接失败

```bash
# 检查 MySQL 状态
docker-compose ps mysql

# 查看 MySQL 日志
docker-compose logs mysql

# 手动连接测试
docker-compose exec mysql mysql -u root -p
```

### 2. Elasticsearch 启动慢

ES 需要较多内存，如果启动失败：
```bash
# 增加 Docker 内存限制
# Docker Desktop -> Settings -> Resources -> Memory: 4GB+
```

### 3. 应用无法连接数据库

确保 `app_config.yaml` 中的 host 使用服务名：
```yaml
db_meta:
  host: mysql  # 不是 localhost
  port: 3306
```

## 🔄 更新部署

```bash
# 拉取最新代码
git pull

# 重新构建并启动
docker-compose up --build -d

# 仅重启应用
docker-compose restart data-agent
```

## 📚 参考文档

- [Data-Agent 系统规格](docs/specs/data-agent-spec.md)
- [Data-Agent 学习笔记](docs/data-agent-learning/1.md)
- [项目操作指南](docs/project-guide.md)
