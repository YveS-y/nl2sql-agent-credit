import asyncio
from typing import Optional

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine, async_sessionmaker

from app.conf.app_config import DBConfig, app_config

# 职责：管理引擎（连接池）和会话工厂的生命周期
class MysqlClientManager:
    # 构造时只存配置，不立即连接数据库（延迟初始化模式）。 import 阶段
    def __init__(self, db_config: DBConfig):
        self.db_config = db_config
        self.engine: Optional[AsyncEngine] = None
        self.session_factory = None

    # 拼接 SQLAlchemy 连接字符串
    def _get_url(self):
        return f"mysql+asyncmy://{self.db_config.user}:{self.db_config.password}@{self.db_config.host}:{self.db_config.port}/{self.db_config.database}?charset=utf8mb4"

    # 初始化引擎和会话工厂 lifespan 阶段
    def init(self):
        self.engine = create_async_engine(url=self._get_url(),
                                          pool_size=10,
                                          # # 每次取连接前先 ping 一下，剔除已断开的死连接
                                          pool_pre_ping=True)
        self.session_factory = async_sessionmaker(self.engine,
                                                  # 查询前自动 flush 待写数据到 DB
                                                  autoflush=True,
                                                  # commit 后对象属性仍可访问，无需重新查
                                                  expire_on_commit=False,
                                                  # session 自动开启事务
                                                  autobegin=True)

    # 关闭引擎，释放连接池中所有连接
    async def close(self):
        await self.engine.dispose()

# 客户端管理器实例，持有元数据库的连接配置（import时就会执行，将配置信息存进这个对象）
dw_mysql_client_manager = MysqlClientManager(app_config.db_dw)
meta_mysql_client_manager = MysqlClientManager(app_config.db_meta)

if __name__ == '__main__':
    meta_mysql_client_manager.init()


    # async def test():
    #     async with meta_mysql_client_manager.session_factory() as session:
    #         result = await session.execute(text("select * from table_info limit 10"))
    #         rows = result.fetchall()
    #         print(rows)


    # asyncio.run(test())
