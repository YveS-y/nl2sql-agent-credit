from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langgraph.runtime import Runtime

from app.agent.context import DataAgentContext
from app.agent.state import DataAgentState
from app.agent.llm import llm
from app.core.log import logger
from app.prompt.prompt_loader import load_prompt


async def clarify_query(state: DataAgentState, runtime: Runtime[DataAgentContext]):
    writer = runtime.stream_writer
    writer({"type": "progress", "step": "理解问题", "status": "running"})

    query = state["query"]

    prompt = PromptTemplate(template=load_prompt("clarify_query"), input_variables=["query"])
    chain = prompt | llm | StrOutputParser()

    result = (await chain.ainvoke({"query": query})).strip()

    if result == "CLEAR":
        writer({"type": "progress", "step": "理解问题", "status": "success"})
        logger.info(f"问题清晰，继续流程: {query}")
        return {"clarification": ""}
    else:
        writer({"type": "progress", "step": "理解问题", "status": "success"})
        writer({"type": "clarification", "question": result})
        logger.info(f"问题模糊，反问: {result}")
        return {"clarification": result}
