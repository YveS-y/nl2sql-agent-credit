import asyncio

from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from langgraph.runtime import Runtime

from app.agent.context import DataAgentContext
from app.agent.llm import llm
from app.agent.state import DataAgentState
from app.core.log import logger
from app.entities.value_info import ValueInfo
from app.prompt.prompt_loader import load_prompt


async def recall_value(state: DataAgentState, runtime: Runtime[DataAgentContext]):
    # 告诉前端目前进度
    writer = runtime.stream_writer
    writer({"type": "progress", "step": "召回字段取值", "status": "running"})

    # 接收用户输入内容和分词内容
    query = state["query"]
    keywords = state["keywords"]

    # 从 context 中取出 es 仓库
    # runtime.context 是一个 传参通道 
    # 启动时把各种仓库对象打包塞进 context 
    # graph 执行时自动传给每个节点，节点里通过runtime.context["xxx"]取出来直接调用
    value_es_repository = runtime.context["value_es_repository"]

    try:
        # 使用LLM扩展关键词
        # 通过预先定义的专门扩写值的提示词模板扩展，输出为json 
        prompt = PromptTemplate(template=load_prompt("extend_keywords_for_value_recall"), input_variables=["query"])
        output_parser = JsonOutputParser()

        chain = prompt | llm | output_parser

        # 开始执行 
        result = await chain.ainvoke({"query": query})

        # 准备一个字典接收这个节点最后的结果
        values_map: dict[str, ValueInfo] = {}
        # 把原始分词和llm扩展结果合并，set去重，list转回列表
        keywords = list(set(keywords + result))
        logger.info(f"召回字段取值扩展关键词：{keywords}")
        # 逐个关键词在 es 中搜索匹配的字段取值
        for keyword in keywords:
            # 在 es 索引中搜索，返回匹配的 ValueInfo 列表
            values: list[ValueInfo] = await value_es_repository.search(keyword)
            # 根据 ValueInfo 主键 id 去重
            for value in values:
                value_id = value.id
                if value_id not in values_map:
                    values_map[value_id] = value

        # 把字典转成列表
        retrieved_values = list(values_map.values())

        writer({"type": "progress", "step": "召回字段取值", "status": "success"})
        logger.info(f"召回字段取值：{list(values_map.keys())}")

        return {'retrieved_values': retrieved_values}
    except Exception as e:
        writer({"type": "progress", "step": "召回字段取值", "status": "error"})
        logger.error(f"召回字段取值失败: {str(e)}")
        raise
