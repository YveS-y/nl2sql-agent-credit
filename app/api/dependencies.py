from fastapi import Depends
# Depends 依赖注入 核心工具
# 写法：参数名: 类型 = Depends(工厂函数) 
# 作用：框架会自动调用工厂函数，把返回值塞到这个参数里
from langchain_huggingface import HuggingFaceEndpointEmbeddings
# 引入 HuggingFace 的 Embedding 客户端类型。本文件只用它做"类型注解"（告诉 IDE 和读者：这个参数是个 Embedding 客户端），并不直接实例化它。
from sqlalchemy.ext.asyncio import AsyncSession
# 引入 SQLAlchemy 的异步会话类型。同样主要用于类型注解，表明某个参数是一个异步数据库会话。

from app.clients.embedding_client_manager import embedding_client_manager
from app.clients.es_client_manager import es_client_manager
from app.clients.mysql_client_manager import meta_mysql_client_manager, dw_mysql_client_manager
from app.clients.qdrant_client_manager import qdrant_client_manager
# 引入 5 个全局单例管理器： 四个"客户端管理器"
# embedding_client_manager —— 向量化模型客户端
# es_client_manager —— Elasticsearch 客户端
# meta_mysql_client_manager —— 元数据 MySQL
# dw_mysql_client_manager —— 数仓 MySQL
# qdrant_client_manager —— Qdrant 向量数据库


from app.repositories.es.value_es_repository import ValueESRepository
from app.repositories.mysql.dw.dw_mysql_repository import DWMySQLRepository
from app.repositories.mysql.meta.meta_mysql_repository import MetaMySQLRepository
from app.repositories.qdrant.column_qdrant_repository import ColumnQdrantRepository
from app.repositories.qdrant.metric_qdrant_repository import MetricQdrantRepository
# 五个仓储类（Repository）
# 仓储层负责封装对某个数据源的查询方法（比如"按关键词搜索列"、"查询指标元数据"）。它们包在客户端外面一层，给业务层提供更友好的接口。

from app.services.query_service import QueryService
# 引入业务服务类 QueryService ——它把多个 Repository 组合起来完成"数据查询"这件事。

# 这个文件是组装说明书：定义了"怎么把底层连接 → 包成 Repository → 再组装成 Service"的完整链路，让路由层拿到的 QueryService 是一个开箱即用、什么都能干的完整对象

async def get_meta_session():
    # 实际是async_sessionmaker 实例，调用时就会创建一个session
    async with meta_mysql_client_manager.session_factory() as session:
        yield session


async def get_dw_session():
    async with dw_mysql_client_manager.session_factory() as session:
        yield session


async def get_embedding_client():
    return embedding_client_manager.client


async def get_column_qdrant_repository():
    return ColumnQdrantRepository(qdrant_client_manager.client)


async def get_value_es_repository():
    return ValueESRepository(es_client_manager.client)


async def get_metric_qdrant_repository():
    return MetricQdrantRepository(qdrant_client_manager.client)


async def get_meta_mysql_repository(session: AsyncSession = Depends(get_meta_session)):
    return MetaMySQLRepository(session)


async def get_dw_mysql_repository(session: AsyncSession = Depends(get_dw_session)):
    return DWMySQLRepository(session)


async def get_query_service(
        embedding_client: HuggingFaceEndpointEmbeddings = Depends(get_embedding_client),
        column_qdrant_repository: ColumnQdrantRepository = Depends(get_column_qdrant_repository),
        value_es_repository: ValueESRepository = Depends(get_value_es_repository),
        metric_qdrant_repository: MetricQdrantRepository = Depends(get_metric_qdrant_repository),
        meta_mysql_repository: MetaMySQLRepository = Depends(get_meta_mysql_repository),
        dw_mysql_repository: DWMySQLRepository = Depends(get_dw_mysql_repository)
) -> QueryService:
    return QueryService(
        embedding_client=embedding_client,
        column_qdrant_repository=column_qdrant_repository,
        value_es_repository=value_es_repository,
        metric_qdrant_repository=metric_qdrant_repository,
        meta_mysql_repository=meta_mysql_repository,
        dw_mysql_repository=dw_mysql_repository
    )