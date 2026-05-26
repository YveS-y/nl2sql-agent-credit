from fastapi import APIRouter
from fastapi.params import Depends
from starlette.responses import StreamingResponse

from app.api.dependencies import get_query_service
from app.api.schemas.query_schema import QuerySchema
from app.services.query_service import QueryService


query_router = APIRouter() # 创建一个空清单

@query_router.post("/api/query") # 手动把这个函数加进清单
async def query(
    query: QuerySchema, query_service: QueryService = Depends(get_query_service)
):
    # 要返回的内容和 SSE 协议
    return StreamingResponse(
        query_service.query(query.query), media_type="text/event-stream"
    )
# query_service.query(query.query)
#    ↑服务实例  ↑方法   ↑参数  ↑字段
#    │          │       │      └─ QuerySchema.query (str) → 用户实际输入的问题文本
#    │          │       └─ 路由函数参数 query: QuerySchema → 整个请求体对象
#    │          └─ QueryService.query() 方法 → 启动 Agent 跑图
#    └─ dependencies 注入的 QueryService 实例