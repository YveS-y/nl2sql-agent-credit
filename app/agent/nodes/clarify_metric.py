from langgraph.runtime import Runtime

from app.agent.context import DataAgentContext
from app.agent.state import DataAgentState
from app.core.log import logger

# 歧义指标 → 追问话术
_AMBIGUOUS_METRICS = {
    "逾期率": "您查询的逾期率是指首逾率(M1)、整体逾期率还是在贷逾期率？",
}

# 包含这些词说明用户已经澄清了口径，不再追问
_CLARIFICATION_KEYWORDS = {"首逾", "M1", "m1", "整体", "在贷", "综合", "累计"}

# 包含这些词说明用户在查明细笔数/记录数，而非在查逾期率指标，跳过歧义追问
# 策略：负向排除（只排除"明显问笔数"的情况），其余一律追问，防止漏追问
_COUNT_QUERY_KEYWORDS = {"多少笔", "笔贷款", "笔逾期", "多少条", "条记录", "记录有多少"}


async def clarify_metric(state: DataAgentState, runtime: Runtime[DataAgentContext]):
    writer = runtime.stream_writer
    writer({"type": "progress", "step": "确认指标口径", "status": "running"})

    metric_infos = state["metric_infos"]
    query = state["query"]

    for metric_info in metric_infos:
        metric_name = metric_info["name"]
        if metric_name in _AMBIGUOUS_METRICS:
            # 用户问题里已包含澄清词，不追问
            if any(kw in query for kw in _CLARIFICATION_KEYWORDS):
                continue
            # 用户明显在查明细笔数/记录数，不是在查率指标，跳过追问
            if any(kw in query for kw in _COUNT_QUERY_KEYWORDS):
                continue
            question = _AMBIGUOUS_METRICS[metric_name]
            writer({"type": "progress", "step": "确认指标口径", "status": "success"})
            writer({"type": "clarification", "question": question})
            logger.info(f"触发歧义指标追问: {metric_name} → {question}")
            return {"clarification_question": question}

    writer({"type": "progress", "step": "确认指标口径", "status": "success"})
    logger.info("指标口径无歧义，继续生成SQL")
    return {"clarification_question": None}
