import yaml
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from langgraph.runtime import Runtime

from app.agent.context import DataAgentContext
from app.agent.llm import llm
from app.agent.state import DataAgentState
from app.core.log import logger
from app.prompt.prompt_loader import load_prompt


async def filter_table(state: DataAgentState, runtime: Runtime[DataAgentContext]):
    writer = runtime.stream_writer
    writer({"type": "progress", "step": "过滤表格", "status": "running"})

    query = state["query"]
    table_infos = state["table_infos"]

    try:
        # 用LLM过滤表信息
        # 调用拿到表过滤的提示词
        prompt = PromptTemplate(template=load_prompt("filter_table_info"), input_variables=["query", "table_infos"])
        # 指示llm输出json格式并自动解析
        output_parser = JsonOutputParser()
        # 使用lcel语法串联调用大模型步骤
        chain = prompt | llm | output_parser
        # 执行并得到返回结果，将 table_infos序列化为yaml文本，方便llm阅读
        result = await chain.ainvoke(
            {"query": query, "table_infos": yaml.dump(table_infos, allow_unicode=True, sort_keys=False)})

        # 利用模型返回结果，对表和字段做二级过滤，过滤table_infos
        # key是表明，value是llm任务这个表需要的字段名列表
        # {
        #   'fact_order':['order_amount', 'region_id'],
        #   'dim_region':['region_id', 'region_name']
        # }
        # 遍历所有表，如果表名不在llm返回的result中，删除该表
        # 遍历[:]浅拷贝，安全地在原列表上删除元素，寻址寻拷贝的列表，操作元素还是原列表
        for table_info in table_infos[:]:
            if table_info["name"] not in result:
                table_infos.remove(table_info)
            else:
                # 如果表保留，再删除llm未选中的字段
                selected_columns = result[table_info["name"]]
                
                for column_info in table_info["columns"][:]:
                    if column_info["name"] not in selected_columns:
                        table_info["columns"].remove(column_info)

        writer({"type": "progress", "step": "过滤表格", "status": "success"})
        logger.info(f"过滤后的表信息: {[table_info['name'] for table_info in table_infos]}")
        return {"table_infos": table_infos}
    except Exception as e:
        writer({"type": "progress", "step": "过滤表格", "status": "error"})
        logger.error(f"过滤表失败:{str(e)}")
        raise
