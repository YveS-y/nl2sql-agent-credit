from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.clients.embedding_client_manager import embedding_client_manager
from app.clients.es_client_manager import es_client_manager
from app.clients.mysql_client_manager import meta_mysql_client_manager, dw_mysql_client_manager
from app.clients.qdrant_client_manager import qdrant_client_manager

# 管理所有数据库连接的开和关
# 这个装饰器把一个带 yield 的普通函数，变成 FastAPI 能识别的生命周期格式。
# FastAPI 规定 lifespan 参数必须是这种格式，所以加了这个装饰器。你现在不需要深入理解它，记住：带 yield 的函数 + 这个装饰器 = FastAPI 认识的生命周期函数。
@asynccontextmanager
async def lifespan(app: FastAPI):
    # FastAPI 应用启动前执行
    # 启动前 ——— 初始化所有数据库连接池（这5行就是提前把所有数据库连接建好，存在内存里备用。）
    embedding_client_manager.init()
    qdrant_client_manager.init()
    es_client_manager.init()
    meta_mysql_client_manager.init()
    dw_mysql_client_manager.init()
    yield   # ← 这里是应用正在运行的阶段
    # FastAPI 应用结束前执行
    # 关闭前 ——— 释放所有连接，fastAPI 会自动调用这些客户端的 close 方法，关闭所有数据库连接

    await qdrant_client_manager.close()
    await es_client_manager.close()
    await meta_mysql_client_manager.close()
    await dw_mysql_client_manager.close()
