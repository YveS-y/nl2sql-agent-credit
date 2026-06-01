from pydantic import BaseModel


class QuerySchema(BaseModel):
    query: str
    conversation_history: list[dict] = []
