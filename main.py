import uuid

from fastapi import FastAPI, Request

from app.api.routers.query_router import query_router
from app.core.context import request_id_ctx_var
from app.core.lifespan import lifespan

'''
【uuid】生成唯一 ID 的标准库
└─ 使用的 API
    └─ uuid.uuid4() → 为每个请求生成唯一标识

【FastAPI】把 Python 函数变成 HTTP 接口的 Web 框架
├─ 核心能力
│   路由匹配、请求解析(JSON→Python)、参数校验、响应序列化(Python→JSON)、自动生成API文档
│   （监听端口是 uvicorn 的活，不是它干的）
├─ 在本项目中的角色
│   把 query_service.query() 暴露成 POST /api/query 接口，让前端能发请求过来
└─ 使用的 API
    ├─ FastAPI(lifespan=...)     → 创建应用实例，绑定生命周期管理
    ├─ app.include_router(...)   → 注册路由，把 /api/query 挂载上来
    ├─ @app.middleware("http")   → 注册中间件，每个请求经过时生成 request_id
    └─ Request, call_next        → 中间件参数，拦截请求和放行

【uvicorn】ASGI 服务器，负责监听端口、接收网络请求、转交给 FastAPI 处理
└─ 使用的 API
    └─ uvicorn.run(app, host, port) → 启动服务器监听
'''

# 创建应用实例，绑定生命周期（启动时初始化数据库连接，关闭时释放）
app = FastAPI(lifespan=lifespan)

# 注册路由
app.include_router(query_router)

# 注册中间件：每个请求进来时生成唯一 request_id，存到 ContextVar 里供后续日志使用
# 流程：请求 → 中间件(生成request_id) → call_next放行 → 路由处理 → 响应返回
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    request_id_ctx_var.set(uuid.uuid4())
    response = await call_next(request)
    return response

'''
整体流程
    │
    ├─ 创建 app
    ├─ lifespan 启动 → 初始化所有数据库连接
    ├─ 注册路由 → /api/query 可以访问了
    ├─ 注册中间件 → 每个请求都会先经过它
    └─ uvicorn 开始监听 8000 端口

收到请求
    │
    ├─ 中间件：生成 request_id
    ├─ 路由：/api/query → query_router
    └─ 返回 SSE 流式响应

程序关闭
    └─ lifespan 关闭 → 释放所有数据库连接
'''

# 只有直接运行本文件时才启动服务器，被 import 时不执行
if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
