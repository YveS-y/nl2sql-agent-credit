from dataclasses import asdict

from qdrant_client import AsyncQdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct

from app.conf.app_config import app_config
from app.entities.column_info import ColumnInfo


class ColumnQdrantRepository:
    collection_name: str = 'data-agent-column' # 集合名（类似 MySQL 的"表名"）

    def __init__(self, client: AsyncQdrantClient):   # 接收外部注入的 Qdrant client
        self.client = client


    # 确保集合存在
    async def ensure_collection(self):
        if not await self.client.collection_exists(self.collection_name):
            await self.client.create_collection(self.collection_name,
                                                vectors_config=VectorParams(size=app_config.qdrant.embedding_size,
                                                                            distance=Distance.COSINE))
    # 批量写入/更新向量
    async def upsert(self, ids: list[str], embeddings: list[list[float]], payloads: list[ColumnInfo],
                     batch_size: int = 20):
        zipped = list(zip(ids, embeddings, payloads))   # 把三个列表打包成元组列表
        for i in range(0, len(zipped), batch_size):     # 每 20 条一批
            batch = zipped[i:i + batch_size]
            # 唯一标识 向量（如 [0.12, -0.03, ...]）  附带的元数据（列名、表名、描述等）
            batch_points = [PointStruct(id=id, vector=embedding, payload=asdict(payload)) for id, embedding, payload in
                            batch]
            await self.client.upsert(collection_name=self.collection_name, points=batch_points)

    async def search(self, embedding: list[float], score_threshold: float = 0.6, limit: int = 5) -> list[ColumnInfo]:
        result = await self.client.query_points(collection_name=self.collection_name,
                                                query=embedding,    # 用这个向量去搜
                                                score_threshold=score_threshold,    # 相似度阈值 < 0.6 的不要
                                                limit=limit)        # 最多返回 5 条
        # 把 Qdrant 返回的原始字典数据（payload），逐个转换成项目定义的 ColumnInfo 类型对象，让上层代码能用 .table_name、.column_name 这样的属性访问，而不是字典的 ["key"] 方式。
        return [ColumnInfo(**point.payload) for point in result.points]
