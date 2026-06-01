from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langgraph.runtime import Runtime

from app.agent.context import DataAgentContext
from app.agent.llm import llm
from app.agent.state import DataAgentState
from app.core.log import logger

_PROMPT = """你是一个查询改写助手。根据对话历史，把用户最新的问题改写成一句完整、自包含的问题。

改写规则（严格遵守）：
1. 如果最新问题已经完整清晰（不含指代），原样返回，不要修改任何内容
2. 把"这个"、"那个"、"它"、"上周呢"、"那呢"、"4月呢"等指代/省略替换成具体内容
3. 维度词（"各"、"每个"、"按渠道"、"分产品"等）必须原样保留，不得省略
4. 时间必须带上年份写成完整格式（如"2026年4月"），禁止裸写"4月"、"上月"
5. 维度名称（渠道名、产品名）和时间表达之间必须用"的"或空格隔开，禁止合并成一个词
6. 只输出改写后的问题本身，不要有任何解释

对话历史（最近3轮）：
{history}

用户最新问题：{query}

改写后的问题："""


# 只有 query 中含有这些词时，才说明它依赖上下文，需要改写
# 不含这些词 → query 自包含 → 直接跳过，避免 LLM 过度联想
_CONTEXT_DEPENDENT_PATTERNS = [
    "呢", "那", "这个", "那个", "它", "上面", "之前",
    "也", "还是",  # "也查一下X" "还是X呢"
]


def _needs_rewrite(query: str) -> bool:
    return any(p in query for p in _CONTEXT_DEPENDENT_PATTERNS)


async def rewrite_query(state: DataAgentState, runtime: Runtime[DataAgentContext]):
    writer = runtime.stream_writer
    writer({"type": "progress", "step": "理解上下文", "status": "running"})

    query = state["query"]
    history = state.get("conversation_history") or []

    # 没有历史记录，无需改写
    if not history:
        writer({"type": "progress", "step": "理解上下文", "status": "success"})
        logger.info("无对话历史，跳过改写")
        return {}

    # query 不含指代词，说明问题自包含，直接跳过，不让 LLM 有机会过度联想
    if not _needs_rewrite(query):
        writer({"type": "progress", "step": "理解上下文", "status": "success"})
        logger.info(f"问题自包含，跳过改写: {query}")
        return {}

    # 取最近3轮（最多6条消息）
    recent = history[-6:]
    history_text = "\n".join(
        f"{'用户' if msg['role'] == 'user' else '助手'}：{msg['content']}"
        for msg in recent
    )

    prompt = PromptTemplate(template=_PROMPT, input_variables=["history", "query"])
    chain = prompt | llm | StrOutputParser()
    rewritten = (await chain.ainvoke({"history": history_text, "query": query})).strip()

    writer({"type": "progress", "step": "理解上下文", "status": "success"})
    logger.info(f"改写查询: '{query}' → '{rewritten}'")
    return {"query": rewritten}
