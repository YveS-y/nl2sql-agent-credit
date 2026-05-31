# data-agent 自测题（47题）

> 使用方法：从上到下逐题作答，答完所有题再翻到下方答案区对照。
> 答不上来的题号记下来，优先回到对应代码节点深读。

---

## 题目区

### 第一组：数据流向（10题）

**Q1.** `filter_table` 和 `filter_metric` 之间直接传递数据吗？它们各自的输入从哪里来？

**Q2.** `correct_sql` 节点什么情况下会被触发？触发条件在代码哪里定义？

**Q3.** Qdrant 和 Elasticsearch 分别用于召回哪类数据？各自解决什么问题？

**Q4.** `recall_column` 输出的列数据，经过哪个节点、什么处理后，才最终出现在 `table_infos` 里？

**Q5.** `retrieved_values` 里的取值是怎么和字段关联起来的？关联字段叫什么？

**Q6.** `keywords` 字段是在哪个节点被赋值的？赋值后立即被哪三个节点消费？

**Q7.** `table_infos` 在整个图执行过程中一共被几个节点修改过？每次修改做了什么？

**Q8.** `merge_retrieved_info` 为什么要补充主外键字段？不补会有什么后果？

**Q9.** `metric_infos` 里的 `relevant_columns` 字段有什么作用？它在哪个节点被用到？

**Q10.** SQL 执行失败的完整处理流程是什么？最多有几次修正机会？

---

### 第二组：设计决策（10题）

**Q11.** 为什么用 LangGraph 而不是写一个函数调用链？说出至少三个 LangGraph 解决了而链式调用解决不了的问题。

**Q12.** State 为什么用 `TypedDict` 而不是 `dataclass` 或普通 `dict`？三者在运行时有什么区别？

**Q13.** 为什么要分三路并行召回（column/value/metric），合并成一路不行吗？每路解决了什么不同的问题？

**Q14.** `filter_table` 的 prompt 输入为什么用 YAML 格式，而不是 JSON？

**Q15.** LLM 的 `temperature` 为什么设为 0？设成 0.7 会有什么影响？

**Q16.** 客户端（Qdrant/ES/MySQL）为什么要用单例模式？不用单例每次新建连接会有什么问题？

**Q17.** 为什么有 Entity 层（dataclass）和 State 层（TypedDict）两套数据结构？能合并成一套吗？

**Q18.** `correct_sql` 之后为什么不再经过 `validate_sql`，直接进入 `execute_sql`？这个设计的代价是什么？

**Q19.** `extract_keywords` 为什么把原始 `query` 也加入 keywords，而不只用 jieba 分词结果？

**Q20.** `merge_retrieved_info` 为什么要把 Entity 的 `id` 字段去掉，转换成 State 格式？

---

### 第三组：实现机制（8题）

**Q21.** LangGraph 是怎么实现三路并行召回的？并行的条件是什么？三路完成后怎么自动汇合？

**Q22.** SSE 流式响应是怎么实现的？从 FastAPI 层到各节点之间的数据流是什么？

**Q23.** `stream_writer` 是怎么传入各节点的？为什么不放在 State 里传递？

**Q24.** FastAPI 的 `Depends` 依赖注入是怎么工作的？`DataAgentContext` 是怎么组装和传入的？

**Q25.** 异步 SQLAlchemy 和同步版本有什么区别？`await session.execute()` 在并发场景下有什么意义？

**Q26.** `build_meta_knowledge.py` 做了什么事情？什么情况下需要重新运行它？

**Q27.** LangGraph 的条件边（`add_conditional_edges`）是怎么定义路由逻辑的？写出 `validate_sql` 之后的条件边代码结构。

**Q28.** 节点函数为什么要用 `async def`？哪些操作真正受益于异步，哪些没有？

---

### 第四组：影响分析（8题）

**Q29.** 如果把 `score_threshold` 从 0.6 改为 0.8，召回结果会怎么变？极端情况下会发生什么？

**Q30.** 如果 `meta_config.yaml` 里的表描述写得很差，会从哪个环节开始出问题？影响链是什么？

**Q31.** 如果去掉 `filter_table` 节点，直接把 `merge_retrieved_info` 的输出给 `generate_sql`，会有什么后果？

**Q32.** 如果 `recall_column` 在执行中抛出了异常，图的执行会怎么走？用户最终看到什么？

**Q33.** 如果同一个字段被 `recall_column` 和 `recall_value` 都召回了，最终 `table_infos` 里会重复吗？为什么？

**Q34.** 如果 LLM 在 `generate_sql` 中编造了一个不存在的表名，`validate_sql` 能检测到吗？怎么检测的？

**Q35.** 如果 `correct_sql` 修正之后 SQL 还是错的，用户会收到什么响应？系统有二次重试吗？

**Q36.** 100 个请求并发进来，`graph` 对象和 `state` 是共享的还是隔离的？为什么？

---

### 第五组：业务理解（6题）

**Q37.** 为什么 NL2SQL 需要做"召回"这一步？不能把所有表结构直接给 LLM 吗？

**Q38.** `value` 召回解决了哪个具体的业务痛点？举一个没有 value 召回时会出错的例子。

**Q39.** 指标（metric）和字段（column）的本质区别是什么？为什么指标需要单独召回？

**Q40.** 分层路由（ADS/DWS/DWD）在信贷场景中是什么含义？为什么要优先选 ADS？

**Q41.** 口径澄清（`clarify_query`）解决了什么业务痛点？触发条件是什么？

**Q42.** 多轮对话（`rewrite_query`）为什么设计在图的第一步，而不是在每个节点里单独处理？

---

### 第六组：可扩展性（5题）

**Q43.** 如果要新增一张信贷业务表（如催收记录表），需要改哪些文件？需要改 Python 代码吗？

**Q44.** 如果要新增一个业务指标（如"净现值收益率"），需要改哪些地方？

**Q45.** 如果要在图中新增一个节点（如 SQL 敏感字段审计），步骤是什么？按什么顺序改？

**Q46.** 如果要把数据库从 MySQL 换成 PostgreSQL，需要改哪些地方？哪些不需要改？

**Q47.** 整个系统最脆弱的环节是哪里？为什么？应该怎么监控和改进？

---

---

---

---

---

---

---

---

---

> 以下是答案区，建议做完所有题目再看。

---

---

---

---

---

---

---

---

---

---

---

## 答案区

---

### 第一组答案

**A1.** 它们**不直接通信**。两者都从 `merge_retrieved_info` 的输出中独立读取：
- `filter_table` 读 `table_infos`，过滤后写回 `table_infos`
- `filter_metric` 读 `metric_infos`，过滤后写回 `metric_infos`
- 两者并行执行，写不同字段，不冲突，全部完成后才进入 `add_extra_context`

---

**A2.** 当且仅当 `validate_sql` 执行 `EXPLAIN {sql}` 抛出异常，将错误信息存入 `state["error"]`，路由函数检测到 `error is not None` 时触发。定义在 `graph.py` 的条件边：
```python
builder.add_conditional_edges(
    "validate_sql",
    lambda state: "execute_sql" if state["error"] is None else "correct_sql",
    {"execute_sql": "execute_sql", "correct_sql": "correct_sql"}
)
```

---

**A3.**
- **Qdrant**（向量检索）：用于 `recall_column`（找语义相关字段名）和 `recall_metric`（找语义相关指标）。用向量相似度匹配"业务语义"，不要求精确字符匹配。
- **ES**（全文检索）：用于 `recall_value`（找精确枚举值，如"自营APP"、"北京"）。枚举值用向量找不准，需要精确文字匹配。

---

**A4.** `recall_column` 输出 `retrieved_columns: list[ColumnInfo]`，由 `merge_retrieved_info` 节点处理：补充指标关联字段、补充枚举值对应字段、补充主外键、按表分组，最终转换为 `table_infos: list[TableInfoState]`。

---

**A5.** 通过 `ValueInfo.column_id` 字段关联。`merge_retrieved_info` 中遍历 `retrieved_values`，用 `value.column_id` 查找对应列，将 `value.value` 追加到该列的 `examples` 列表。如果该列还不在 `retrieved_columns_map` 中，则先从 meta 库查出来再追加。

---

**A6.** 在 `extract_keywords` 节点赋值，内容 = jieba 分词结果 + 原始 query，set 去重。赋值后同时被三个并行节点消费：`recall_column`、`recall_value`、`recall_metric`。

---

**A7.** 两次修改：
1. `merge_retrieved_info`：创建 `table_infos`，补充主外键，格式从 Entity 转为 State
2. `filter_table`：LLM 过滤，删除不需要的表和字段

`add_extra_context`、`generate_sql`、`correct_sql` 只读 `table_infos`，不写。

---

**A8.** 支持多表 JOIN：SQL 的 JOIN 条件需要主键和外键。如果召回到了两张表但没有它们之间的关联字段，`generate_sql` 无法写出正确的 JOIN 条件，SQL 会出错。`merge_retrieved_info` 自动补充这些关联键，确保 LLM 有足够信息写 JOIN。

---

**A9.** `relevant_columns` 是指标的依赖字段列表（如"逾期率"依赖 `overdue_amount` 和 `due_amount`）。在 `merge_retrieved_info` 节点中被用到：遍历每个指标的 `relevant_columns`，如果这些字段还没在 `retrieved_columns_map` 里，则主动从 meta 库补充进来，确保 LLM 能看到计算指标所需的字段。

---

**A10.** 两步：① `validate_sql` 执行 `EXPLAIN`，如失败，将错误写入 `state["error"]`，路由到 `correct_sql`；② `correct_sql` 读取错误信息，LLM 最小化修正，输出新 SQL，直接进入 `execute_sql`。**最多修正一次**，修正后不再验证，直接执行。

---

### 第二组答案

**A11.** 三个 LangGraph 解决、链式调用难以处理的问题：
1. **条件分支**：`validate_sql` 根据 `error` 是否为 None 路由到不同节点，链式调用需手写 if-else 嵌套，状态传递混乱
2. **并行执行**：三路召回同时运行，链式调用需手写 `asyncio.gather`，且状态管理需自行协调
3. **共享状态**：12个节点共享同一个 State dict，链式调用需要把状态一层层传参，函数签名膨胀

---

**A12.**
- `TypedDict`：运行时是普通 `dict`（LangGraph 直接操作），但写代码时有类型提示和 IDE 检查
- `dataclass`：运行时是对象（不是 dict），LangGraph 无法直接操作，需要额外适配层
- 普通 `dict`：运行时也是 dict，但没有类型提示，字段名拼错 IDE 不会报警

LangGraph 要求 State 在运行时必须是 dict，TypedDict 满足这个要求同时保留类型安全。

---

**A13.** 三路不能合并，因为分别解决不同层面：
- **column（Qdrant）**：语义相关字段名，用向量相似度，处理"放款额"→`loan_amount`
- **value（ES）**：精确枚举值，用全文检索，处理"自营APP"这种字面值，向量找不准
- **metric（Qdrant）**：业务计算规则，指标不在任何字段名里，需要单独存储和召回

缺任何一路：缺 column 找不到字段；缺 value WHERE 条件写错枚举值；缺 metric 不知道计算公式。

---

**A14.** YAML 对 LLM 更友好：① 无引号无括号，结构更清晰（比相同内容的 JSON 少约 30% token）；② 实验表明 LLM 在 YAML 格式下做字段选择的准确率高于 JSON；③ 多层嵌套时 YAML 缩进比 JSON 花括号更直观。

---

**A15.** SQL 生成是确定性任务，同一个问题每次必须得到相同 SQL，便于测试（跑30个用例每次结果一致）。设成 0.7 会引入随机性，相同查询可能生成不同 SQL，出错时难以复现，自动化测试结果不稳定。

---

**A16.** 连接建立成本高（TCP握手 + 认证 + 连接池初始化，需要 100ms+），不能每个请求新建。单例模式确保：① 连接只在 `lifespan` 启动时创建一次；② 连接池在全进程共享，多个请求复用已有连接；③ 初始化逻辑只执行一次。

---

**A17.** 不能合并，职责不同：
- **Entity（含 id）**：Repository 层做 DB 操作时需要 id（外键关联、查询条件）
- **State（去掉 id）**：给 LLM 看的上下文，id 是 UUID，对 LLM 无意义，会增加 token 噪声，还可能被 LLM 误用在 SQL 里

`merge_retrieved_info` 做的核心工作就是 Entity→State 的转换：去掉 id，补充关联数据，重组结构。

---

**A18.** 避免死循环：如果 `correct_sql` 后再走 `validate_sql`，修正失败则再次路由到 `correct_sql`，可能无限循环。设计假设 LLM 一次修正足够。代价：修正失败时 `execute_sql` 抛异常，用户看到数据库错误信息，需要重新提问。这是有意的简化，以可用性换设计简洁。

---

**A19.** jieba 可能过度切分，如"逾期率"被切成"逾期"+"率"，原始短语的语义向量与完整概念更接近。加入原始 query 后：jieba 分词（细粒度）+原始短语（整体语义）合并去重，召回时既覆盖细粒度词又保留完整语义匹配。

---

**A20.** 三个原因：① UUID 对 LLM 无语义，增加 token 消耗；② 暴露 DB 内部 id 可能被 LLM 误用（如在 SQL 的 WHERE 中引用 UUID）；③ State 只保留业务语义字段（name/type/description/role/examples），这才是 LLM 生成 SQL 时需要的信息。

---

### 第三组答案

**A21.** 在 `graph.py` 中，从 `extract_keywords` 出发写三条边（fan-out），LangGraph 自动检测三个目标节点写不同 state 字段（`retrieved_columns`/`retrieved_values`/`retrieved_metrics`），满足并行条件，自动并行执行。三条边都指向 `merge_retrieved_info`，LangGraph 等所有上游节点完成后自动触发（fan-in）。

---

**A22.** `query_router.py` 返回 `StreamingResponse(async_generator, media_type="text/event-stream")`。async generator 调用 `graph.astream()`，图执行过程中各节点通过 `stream_writer` 推送事件，generator 将每个事件格式化为 `data: {json}\n\n` 输出。客户端用 EventSource 逐帧接收。

---

**A23.** 通过 LangGraph 的 `config["configurable"]` 字典传递，而不走 State。原因：① State 是业务数据，writer 是基础设施对象，混入会污染 State 定义；② State 可能被序列化，writer 不可序列化；③ `config` 是 LangGraph 提供的专门传递执行上下文（非业务数据）的通道。

---

**A24.** FastAPI 在调用路由函数前，先调用 `Depends(create_context)` 中的工厂函数。`create_context()` 从各单例 manager 获取 client 实例，组装 Repository，再组装 `DataAgentContext` 对象，注入到路由函数参数中。好处：路由函数不直接依赖单例，测试时可替换为 mock。

---

**A25.** 同步版阻塞等待 DB 响应，进程卡住；异步版 `await` 时让出 CPU，其他协程可以运行。在三路并行召回场景：三路各自 `await` Qdrant/ES/MySQL，实际并发执行，总耗时 = 最慢那路，而非三路之和。如果是同步，总耗时 = 三路之和。

---

**A26.** 读取 `meta_config.yaml` → 生成文本描述 → 向量化 → 存入 Qdrant（column/metric 集合）→ 存入 ES（value 枚举值）→ 存入 meta MySQL（结构化元数据）。需要重跑的场景：新增/修改表定义或列描述（Qdrant 索引更新）、新增枚举值（ES 更新）、修改指标定义（Qdrant 更新）。只改 prompt 文件不需要重跑。

---

**A27.**
```python
def route_after_validate(state: DataAgentState) -> str:
    return "execute_sql" if state["error"] is None else "correct_sql"

builder.add_conditional_edges(
    source="validate_sql",
    path=route_after_validate,
    path_map={
        "execute_sql": "execute_sql",
        "correct_sql": "correct_sql",
    }
)
```
`validate_sql` 完成后，LangGraph 调用 `route_after_validate(state)` 得到目标节点名，路由过去。

---

**A28.** 真正受益于异步的操作（有 IO 等待）：LLM API 调用（HTTP）、Qdrant 查询（HTTP/gRPC）、ES 查询（HTTP）、MySQL 查询（TCP）。不受益：`jieba.analyse.extract_tags()`（纯 CPU 计算，没有 IO）。但为统一节点函数签名，`extract_keywords` 也写成 `async def`，不影响正确性。

---

### 第四组答案

**A29.** 召回精度提升但召回率下降。极端情况：所有候选字段相似度都低于 0.8 → `retrieved_columns` 为空 → `merge_retrieved_info` 输出空 `table_infos` → `filter_table` 没有候选表 → `generate_sql` 收到空 schema → LLM 无法生成有效 SQL 或生成乱序 SQL。建议通过测试用例实验确定最优阈值。

---

**A30.** 影响链从召回阶段开始传递：① 召回：向量索引质量差 → 与用户查询的向量相似度低 → 漏召回关键字段；② 过滤：`filter_table` prompt 中候选表描述模糊 → LLM 做出错误选择；③ 生成：`generate_sql` 缺乏字段语义 → 生成语义错误但语法正确的 SQL → `validate_sql` 不报错但结果数据错误。**最危险的是第三步**：完全静默失败，系统"正常运行"但数据错误。

---

**A31.** 三个问题：① **Token 超限**：20张表×20列的全量 YAML 上下文可能超出 LLM 8k/16k token 限制，直接报错；② **准确率下降**：无关列越多，LLM 误选概率越高（注意力稀释）；③ **成本上升**：每次查询消耗 token 是有过滤时的 5-10 倍。

---

**A32.** 节点内部有 `try-except`，捕获异常后向 `stream_writer` 发送错误进度事件，返回空列表 `{"retrieved_columns": []}` 继续流程。图不中断。后果：`table_infos` 可能很少或为空 → `generate_sql` 上下文不完整 → 最终 SQL 错误或无法生成。用户看到 execute_sql 的错误响应，而不是服务崩溃。

---

**A33.** 不会重复。`merge_retrieved_info` 用 `dict`（key 为 `column_id`）存储所有列，同一列被多路召回只存一份。`recall_value` 召回的贡献是：把枚举值（如"自营APP"）追加到该列的 `examples` 列表里，而不是重新添加一列。

---

**A34.** 能。`EXPLAIN {sql}` 在 MySQL 中会验证表是否存在：若 LLM 写了 `fact_loan_record` 但表不存在，MySQL 报错 "Table 'dw.fact_loan_record' doesn't exist"，异常被捕获存入 `state["error"]`，路由到 `correct_sql`。EXPLAIN 能检测：表不存在、字段不存在、语法错误。**不能检测**：语法正确但语义错误（算了错误字段但 SQL 本身合法）。

---

**A35.** `execute_sql` 执行失败，节点 `except` 块捕获，通过 `stream_writer` 发送 `{"type": "error", "message": "SQL执行失败: ..."}` 给客户端。**没有二次重试**，系统不会自动再修正。用户需要重新提问或用更明确的描述。这是有意的边界：无限重试会导致不可预测的延迟和高 API 成本。

---

**A36.** `graph` 对象（编译后的 `CompiledGraph`）全进程共享（只读，类似"函数定义"）。每次 `graph.astream(state, config)` 调用创建独立的 `state` dict（执行上下文隔离）。100 个请求 = 100 个独立 state，互不影响。客户端连接池也是共享的，这正是单例模式的目的——多个请求共享有限的连接资源。

---

### 第五组答案

**A37.** 两个核心约束：① **Token 超限**：信贷系统可能有20-50张表，每张20-50列，全量 schema 约 5-10 万 token，远超 LLM 4k-16k 上下文窗口；② **准确率**：即使能放进去，无关表/列越多，LLM 误选概率越高。召回是"精准上下文构建"，从可能的1000个字段中找出最相关的20-30个给 LLM，是 NL2SQL 在真实业务系统上能用的核心技术。

---

**A38.** 解决"枚举值对不上"问题。例：用户说"查自营APP渠道放款量"，数据库实际枚举值是 `'自营APP'`。没有 value 召回，LLM 可能生成 `WHERE channel = 'APP'` 或 `WHERE channel = '自营'`，查询返回0行，用户误以为没有数据。有 value 召回，ES 精确检索到 `'自营APP'`，加入 `channel` 字段的 `examples`，LLM 生成精确的 `WHERE channel = '自营APP'`。

---

**A39.** 指标是"计算规则"，不是字段：`逾期率 = overdue_amount / due_amount × 100%`。数据库里没有叫"逾期率"的字段，这个公式存在 `meta_config` 的 metric description 里。字段召回找不到它（Qdrant 里没有这个字段向量）。指标召回的价值：① 告诉 LLM 计算公式；② 自动把 `relevant_columns` 里的字段补充进 `table_infos`；③ 统一全公司口径。

---

**A40.**
- **ADS**：已聚合的结果表（"上月逾期率=3.2%"已算好），查询极低代价（几行）
- **DWS**：按渠道/产品/月份汇总，需要 GROUP BY，中等代价（几千行）
- **DWD**：30000条原始明细，需全表扫描，高代价

优先选 ADS 的原因：避免重复扫描明细数据。ADS 已算好结果，直接查一条记录即可。这是数据仓库的最佳实践，`filter_table` 的 prompt 里写了 ADS>DWS>DWD 的优先规则。

---

**A41.** 信贷指标定义模糊，不同口径差异巨大（"逾期率"可以是首逾率≈2.1% 或在贷逾期率≈3.8%，差别接近两倍）。直接查可能用错口径导致业务决策失误。触发条件：① 查询中涉及 meta_config 里标记了 `ambiguous: true` 的指标；② 用户没有提供澄清词（首逾/M1/M2/在贷/累计）。同时满足才追问，避免每次都打断用户。

---

**A42.** 单一职责原则：多轮上下文引用（"这个呢？"/"换成上周"）在第一步统一解决，后续12个节点收到的都是完整、自包含的查询，完全不需要感知多轮上下文。如果分散到每个节点处理，12个节点每个都要复杂一倍，且处理逻辑不一致时容易出bug。

---

### 第六组答案

**A43.** **只改 `conf/meta_config.yaml`**，不改任何 Python 代码。新增表的字段定义（name/role/description/layer/columns），然后运行 `build_meta_knowledge.py` 重新索引（Qdrant + ES + meta MySQL）。这是元数据驱动设计的核心价值：数据模型变化不需要改业务代码。

---

**A44.** 同样**只改 `conf/meta_config.yaml`** 的 `metrics` 部分，添加指标名、描述（含计算公式）、`relevant_columns`、别名，运行 `build_meta_knowledge.py`。指标的计算逻辑写在 description 里，LLM 读取后自动翻译成 SQL 聚合函数，无需改代码。

---

**A45.** 按顺序：① `state.py` 添加新字段（如 `audit_passed: bool`）；② 新建 `app/agent/nodes/audit_sql.py`，函数读 `state["sql"]`，返回 `{"audit_passed": True/False}`；③ `graph.py` 中 `add_node("audit_sql", audit_sql)`，调整边的连接（在 `generate_sql` 和 `validate_sql` 之间插入），添加条件边处理 `audit_passed=False` 的情况。顺序：state → node → graph（因为 node 依赖 state 字段定义）。

---

**A46.** **需要改**：`app_config.yaml`（`dialect` 和连接串）、可能需要改 `mysql_client_manager.py`（连接驱动从 `aiomysql` 换为 `asyncpg`）。**不需要改**：所有节点逻辑、所有 Repository 接口（SQLAlchemy 屏蔽了方言差异）、Entity/State 定义、Qdrant/ES 部分、`generate_sql.prompt`（已经接收 `db_info.dialect`，LLM 自动调整 SQL 方言）。

---

**A47.** **最脆弱**：`meta_config.yaml` 的描述质量。原因：① 是整个系统的知识基础，召回向量全来自这里；② 代码写错有编译器报警，描述写差完全没有提示；③ 出错时全链路"正常运行"但数据结果错误（静默失败，最危险）。监控方法：建立30个测试用例评估集，持续监控字段召回率和 SQL 准确率，发现下滑及时迭代元数据描述。其次脆弱的是 `filter_table` 的 LLM 决策（过度过滤后无法恢复）。
