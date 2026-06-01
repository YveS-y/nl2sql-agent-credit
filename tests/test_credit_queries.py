"""
B7 信贷 NL2SQL 回归测试
目标：30 个用例，至少 25 个通过

运行方式：
  uv run python tests/test_credit_queries.py

判断标准：
  - data    : 收到非空 result 事件（行数 > 0）
  - clarify : 收到 clarification 事件（不应直接出 SQL）
  - empty_ok: 收到 result 事件（允许空结果，只要没报错）
"""

import asyncio
import json
import httpx

API_URL = "http://localhost:8000/api/query"

# ────────────────────────────────────────────────────────────────
# 测试用例定义
# 格式：(编号, 描述, 查询, 期望类型, conversation_history)
# 期望类型：
#   "data"     = 有非空 result
#   "clarify"  = 触发追问（收到 clarification 事件）
#   "empty_ok" = 有 result（允许空）
# ────────────────────────────────────────────────────────────────
CASES = [
    # ── 类别1：简单聚合（ADS层，8个）──────────────────────────────
    (1,  "上月各渠道放款总额",
         "上个月各渠道放款总额是多少",         "data",    []),
    (2,  "上月放款笔数最多的渠道Top3",
         "上月放款笔数最多的前3个渠道",         "data",    []),
    (3,  "自营APP上月平均放款金额",
         "自营APP上个月的平均放款金额",         "data",    []),
    (4,  "2026年1月各渠道放款金额",
         "2026年1月各渠道放款金额",            "data",    []),
    (5,  "上月各渠道首逾率",
         "上月各渠道的首逾率分别是多少",        "data",    []),
    (6,  "2026年以来各月放款趋势",
         "2026年以来每个月的放款总额趋势",      "data",    []),
    (7,  "消费分期12期上月放款额",
         "消费分期12期上个月的放款金额",        "data",    []),
    (8,  "上月放款金额最高前3渠道",
         "昨天放款金额最高的前3个渠道和放款金额", "data",   []),

    # ── 类别2：多维分析（8个）──────────────────────────────────────
    (9,  "各产品各渠道5月放款对比",
         "2026年5月各渠道各产品的放款金额对比",  "data",   []),
    (10, "自营APP和京东金融上月放款对比",
         "自营APP和京东金融上个月放款额对比",    "data",   []),
    (11, "各渠道近3个月放款趋势",
         "各渠道近3个月的放款金额趋势",         "data",   []),
    (12, "消费分期12期各渠道逾期情况",
         "消费分期12期在各渠道的整体逾期率",     "data",   []),
    (13, "线下渠道上月放款总额",
         "线下门店渠道上个月放款总额",          "data",   []),
    (14, "2026年Q1各产品放款笔数",
         "2026年第一季度各产品放款笔数",        "data",   []),
    (15, "上月各渠道整体逾期率排名",
         "上月各渠道整体逾期率从高到低排名",     "data",   []),
    (16, "小额消费贷3期回收率",
         "小额消费贷3期的回收率是多少",         "data",   []),

    # ── 类别3：明细查询（DWD层，4个）─────────────────────────────
    (17, "逾期超过60天的贷款",
         "找出逾期超过60天的贷款记录有多少笔",   "data",   []),
    (18, "昨天放款明细",
         "昨天一共放了多少笔贷款",              "data",   []),
    (19, "还款中贷款平均金额",
         "当前还款中的贷款平均放款金额是多少",   "data",   []),
    (20, "坏账贷款笔数",
         "目前有多少笔贷款状态是坏账",          "data",   []),

    # ── 类别4：口径澄清触发（5个）────────────────────────────────
    (21, "逾期率是多少（应追问）",
         "逾期率是多少",                       "clarify", []),
    (22, "各渠道逾期率对比（应追问）",
         "各渠道逾期率对比",                   "clarify", []),
    (23, "上月逾期率高吗（应追问）",
         "上月逾期率高吗",                     "clarify", []),
    (24, "违约率怎么样（逾期率别名，应追问）",
         "最近违约率怎么样",                   "clarify", []),
    (25, "5月逾期情况（应追问）",
         "2026年5月逾期情况怎么样",            "clarify", []),

    # ── 类别5：多轮对话（5个）────────────────────────────────────
    (26, "多轮：抖音上月放款额（承接渠道追问）",
         "抖音呢",                             "data",
         [{"role": "user",      "content": "自营APP上个月放款额"},
          {"role": "assistant", "content": "自营APP上月放款额为..."}]),

    (27, "多轮：各渠道2月首逾率（承接月份追问）",
         "2月呢",                              "data",
         [{"role": "user",      "content": "各渠道2026年1月首逾率"},
          {"role": "assistant", "content": "已返回2026年1月首逾率..."}]),

    (28, "多轮：消费分期6期放款笔数（承接产品切换）",
         "消费分期6期呢",                       "data",
         [{"role": "user",      "content": "消费分期12期上月放款笔数"},
          {"role": "assistant", "content": "消费分期12期上月放款笔数为..."}]),

    (29, "多轮：回答追问后继续查首逾率",
         "首逾率",                              "data",
         [{"role": "user",      "content": "逾期率是多少"},
          {"role": "assistant", "content": "您查询的逾期率是指首逾率(M1)、整体逾期率还是在贷逾期率？"}]),

    (30, "多轮：那4月呢（承接渠道5月放款）",
         "那4月呢",                             "data",
         [{"role": "user",      "content": "各渠道2026年5月放款额"},
          {"role": "assistant", "content": "已返回各渠道5月放款额..."}]),
]


async def run_case(client: httpx.AsyncClient, case: tuple) -> dict:
    idx, desc, query, expect, history = case
    events = []

    try:
        async with client.stream(
            "POST", API_URL,
            json={"query": query, "conversation_history": history},
            timeout=60,
        ) as resp:
            buf = ""
            async for chunk in resp.aiter_text():
                buf += chunk
                while "\n\n" in buf:
                    evt, buf = buf.split("\n\n", 1)
                    line = evt.strip()
                    if line.startswith("data:"):
                        try:
                            events.append(json.loads(line[5:].strip()))
                        except json.JSONDecodeError:
                            pass
    except Exception as e:
        return {"idx": idx, "desc": desc, "pass": False, "reason": f"请求异常: {e}"}

    # 分析收到的事件
    has_clarification = any(e.get("type") == "clarification" for e in events)
    has_error         = any(e.get("type") == "error"         for e in events)
    result_events     = [e for e in events if e.get("type") == "result"]
    has_result        = bool(result_events)
    result_nonempty   = has_result and len(result_events[0].get("data", [])) > 0
    sql_events        = [e for e in events if e.get("type") == "sql"]
    sql               = sql_events[0]["content"] if sql_events else ""

    if has_error:
        err_msg = next((e.get("message","") for e in events if e.get("type")=="error"), "")
        return {"idx": idx, "desc": desc, "pass": False,
                "reason": f"返回error事件: {err_msg}", "sql": sql}

    if expect == "clarify":
        passed = has_clarification
        reason = "✓ 触发追问" if passed else f"✗ 未触发追问，生成了SQL: {sql}"
    elif expect == "data":
        passed = result_nonempty
        reason = "✓ 返回非空结果" if passed else (
            "✗ 结果为空（数据缺失或SQL条件过严）" if has_result
            else f"✗ 无result事件，SQL: {sql}"
        )
    else:  # empty_ok
        passed = has_result
        reason = "✓ 有result事件" if passed else f"✗ 无result事件，SQL: {sql}"

    return {"idx": idx, "desc": desc, "pass": passed, "reason": reason, "sql": sql}


async def main():
    print("=" * 60)
    print("B7 信贷 NL2SQL 回归测试")
    print("=" * 60)

    results = []
    async with httpx.AsyncClient() as client:
        for case in CASES:
            print(f"\n[{case[0]:02d}] {case[1]} ...", end=" ", flush=True)
            r = await run_case(client, case)
            results.append(r)
            status = "PASS" if r["pass"] else "FAIL"
            print(status)
            if not r["pass"]:
                print(f"      原因: {r['reason']}")
                if r.get("sql"):
                    print(f"      SQL:  {r['sql'][:120]}")

    passed = sum(1 for r in results if r["pass"])
    total  = len(results)

    print("\n" + "=" * 60)
    print(f"结果汇总：{passed}/{total} 通过")
    print("=" * 60)

    fail_list = [r for r in results if not r["pass"]]
    if fail_list:
        print("\n失败用例：")
        for r in fail_list:
            print(f"  [{r['idx']:02d}] {r['desc']}")
            print(f"       {r['reason']}")

    return passed, total


if __name__ == "__main__":
    asyncio.run(main())
