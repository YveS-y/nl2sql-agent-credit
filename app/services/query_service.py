import json

from langchain_huggingface import HuggingFaceEndpointEmbeddings

from app.agent.context import DataAgentContext
from app.agent.graph import graph
from app.agent.state import DataAgentState
from app.repositories.es.value_es_repository import ValueESRepository
from app.repositories.mysql.dw.dw_mysql_repository import DWMySQLRepository
from app.repositories.mysql.meta.meta_mysql_repository import MetaMySQLRepository
from app.repositories.qdrant.column_qdrant_repository import ColumnQdrantRepository
from app.repositories.qdrant.metric_qdrant_repository import MetricQdrantRepository


class QueryService:
    # 收依赖，存起来
    def __init__(self,
                 embedding_client: HuggingFaceEndpointEmbeddings,
                 column_qdrant_repository: ColumnQdrantRepository,
                 value_es_repository: ValueESRepository,
                 metric_qdrant_repository: MetricQdrantRepository,
                 meta_mysql_repository: MetaMySQLRepository,
                 dw_mysql_repository: DWMySQLRepository):
        self.embedding_client = embedding_client
        self.column_qdrant_repository = column_qdrant_repository
        self.value_es_repository = value_es_repository
        self.metric_qdrant_repository = metric_qdrant_repository
        self.meta_mysql_repository = meta_mysql_repository
        self.dw_mysql_repository = dw_mysql_repository


    # 真正干活的业务方法
    async def query(self, query: str, conversation_history: list[dict] = None):
        context = DataAgentContext( # 把依赖再打包成 Agent 的上下文
            embedding_client=self.embedding_client,
            column_qdrant_repository=self.column_qdrant_repository,
            value_es_repository=self.value_es_repository,
            metric_qdrant_repository=self.metric_qdrant_repository,
            meta_mysql_repository=self.meta_mysql_repository,
            dw_mysql_repository=self.dw_mysql_repository
        )
        state = DataAgentState(query=query, conversation_history=conversation_history or []) # 把用户问题包成初始状态
        try:
            # 异步生成器 + for chunk 每次graph输出就处理一下，返回一次
            async for chunk in graph.astream(input=state, context=context, stream_mode="custom"):
                # 生成器，每 yield 一次 → 吐一段给 
                # json.dumps()把 Python 对象序列化成 JSON 字符串（中文不转义、日期等特殊类型强转 str）
                # f"data: {...}\n\n" = 套上 SSE 协议的固定格式（必须以 data: 开头、\n\n 结尾），浏览器才能识别。
                yield f"data: {json.dumps(chunk, ensure_ascii=False, default=str)}\n\n" # SSE格式发送数据
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)}, ensure_ascii=False, default=str)}\n\n" 
