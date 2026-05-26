from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


class DWMySQLRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_column_types(self, table_name: str) -> dict[str, str]:
        sql = f"show columns from {table_name}"
        result = await self.session.execute(text(sql))
        return {row.Field: row.Type for row in result.fetchall()}

    async def get_column_values(self, table_name: str, column_name: str, limit: int):
        sql = f"select distinct {column_name} from {table_name} limit {limit}"
        result = await self.session.execute(text(sql))
        return result.scalars().fetchall()

    async def get_db_info(self):
        result = await self.session.execute(text("select version()"))
        version = result.scalar()

        dialect = self.session.get_bind().dialect.name

        return {'version': version, 'dialect': dialect}

    async def validate_sql(self, sql):
        await self.session.execute(text(f"explain {sql}"))

    async def execute_sql(self, sql):
        result = await self.session.execute(text(sql))
        return [dict(row) for row in result.mappings().fetchall()]


'''
· RowMapping 不是 Python 原生 dict！
result = await self.session.execute(text(sql))   # ① 拿到 Result 对象
rows   = result.mappings()                        # ② 切换成"映射风格"
all    = rows.fetchall()                          # ③ 把所有行拉到内存
为啥要 dict(row) 再转？
① RowMapping 不能 json.dumps → 前端推送会炸
② 切断对 SQLAlchemy 的依赖 → 上层只看到纯 dict
③ 解绑 session 生命周期 → session 关了数据还在
'''