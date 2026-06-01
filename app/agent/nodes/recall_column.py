from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from langgraph.runtime import Runtime

from app.agent.context import DataAgentContext
from app.agent.llm import llm
from app.agent.state import DataAgentState
from app.core.log import logger
from app.entities.column_info import ColumnInfo
from app.prompt.prompt_loader import load_prompt


async def recall_column(state: DataAgentState, runtime: Runtime[DataAgentContext]):
    writer = runtime.stream_writer
    writer({"type": "progress", "step": "召回字段", "status": "running"})

    query = state["query"]
    keywords = state["keywords"]

    embedding_client = runtime.context["embedding_client"]
    column_qdrant_repository = runtime.context["column_qdrant_repository"]

    try:
        # 使用LLM扩展关键词
        # 此时 prompt 对象内部存储的是：
        #   模板文本（固定的）
        #   变量列表 ["query"]
        # 调用时才拼接（运行时替换）
        prompt = PromptTemplate(
            template=load_prompt("extend_keywords_for_column_recall"),
            input_variables=["query"],
        )

        # Prompt 负责"引导"，Parser 负责"解析和容错"
        # 它是标准化处理层，既解析又容错
        output_parser = JsonOutputParser()

        chain = prompt | llm | output_parser

        result = await chain.ainvoke({"query": query})

        # 使用扩展后的关键词召回字段信息
        retrieved_columns_map: dict[str, ColumnInfo] = {}

        # jieba 提取的原始词 和 LLM 扩展的同义词 合并在一起，去重后形成最终的搜索关键词列表
        keywords = list(set(keywords + result))
        logger.info(f"召回字段信息扩展关键词：{keywords}")
        for keyword in keywords:
            # 文本转化向量（aembed_query异步单条嵌入），批量嵌入可改为 aembed_documents
            embedding = await embedding_client.aembed_query(keyword)
            # 将向量传入 qdrant，检索(search)相似字段信息 
            # 
            payloads: list[ColumnInfo] = await column_qdrant_repository.search(
                embedding
            )
            # 根据表中主键id，写入字典实现去重
            for payload in payloads:
                column_id = payload.id
                if column_id not in retrieved_columns_map:
                    retrieved_columns_map[column_id] = payload
        # 再把值放到列表
        retrieved_columns = list(retrieved_columns_map.values())

        # 把这个节点进度给前端、日志，并返回给state
        writer({"type": "progress", "step": "召回字段", "status": "success"})
        logger.info(f"召回字段信息：{list(retrieved_columns_map.keys())}")
        return {"retrieved_columns": retrieved_columns}
    except Exception as e:
        # try块中llm调用扩展关键词，qdrant搜索都可能失败，失败就报错给前端和写入日志
        writer({"type": "progress", "step": "召回字段", "status": "error"})
        logger.error(f"召回字段信息失败: {str(e)}", exc_info=True)
        # 将异常继续向上抛出，告诉LangGraph这里出错了
        raise
