# data-agent-credit — Claude 上下文

## 这个项目是什么

这是一个 NL2SQL Agent，基于 LangGraph 实现，让用户用自然语言查询信贷业务数据库。

**当前状态**：从 nl2sql-agent（电商版）复制过来，**代码已跑通但数据是电商数据**。
**目标**：把数据、元数据、Prompt、新增节点全部换成信贷业务版本。

## 技术栈

| 组件 | 技术 | 说明 |
|------|------|------|
| 工作流引擎 | LangGraph StateGraph | 12节点有状态图 |
| 向量库 | Qdrant | 召回字段名和指标（语义） |
| 搜索引擎 | Elasticsearch | 召回枚举值（精确） |
| 元数据库 | MySQL (meta库) | 存储表/列/指标定义 |
| 数据仓库 | MySQL (dw库) | 实际信贷业务数据 |
| 嵌入模型 | BAAI/bge-large-zh-v1.5 | 文本向量化 |
| API框架 | FastAPI + SSE | 流式响应 |

## 信贷业务背景

- **场景**：个人消费贷，分期还款
- **产品**（3个）：消费分期12期 / 消费分期6期 / 小额消费贷3期
- **渠道**（5个）：自营APP / 京东金融 / 抖音 / 线下门店-北京 / 线下门店-上海
- **数据规模**：6个月历史，约30000笔放款记录

## 数据仓库分层

| 层 | 说明 | 查询代价 | 适合查询 |
|----|------|---------|---------|
| ADS | 已聚合的结果表（月度指标已算好） | 极低 | "上月逾期率是多少" |
| DWS | 按渠道/产品/月份汇总 | 中 | "各渠道放款额对比" |
| DWD | 30000条原始放款明细 | 高 | "找出所有逾期用户" |

**filter_table 规则：优先选 ADS，有现成汇总就不走 DWD。**

## 项目目录结构（关键文件）

```
data-agent-credit/
├── CLAUDE.md                        ← 你现在在读的文件
├── _改造计划/                        ← 改造任务和参考资料
│   ├── 任务清单.md                   ← B1-B7 详细任务（从这里开始）
│   ├── 业务设计/
│   │   ├── 信贷表结构设计.md         ← 信贷数据库表设计
│   │   └── 信贷指标定义.md           ← 信贷业务指标口径
│   └── 参考/
│       └── data-agent-spec.md       ← 完整改造规格说明
├── conf/
│   ├── app_config.yaml              ← 连接配置（不改）
│   └── meta_config.yaml            ← 元数据（B3 全部替换）
├── docker/mysql/init/
│   └── 02_create_dw_tables.sql     ← 建表SQL（B1 全部替换）
├── app/agent/
│   ├── state.py                    ← 状态定义（B4/B5 新增字段）
│   ├── graph.py                    ← 图结构（B4/B5 新增节点和边）
│   └── nodes/                      ← 12个节点（B4/B5 新增2个）
├── prompts/
│   └── filter_table_info.prompt    ← B6 新增分层路由规则
├── app/api/schemas/query_schema.py  ← B5 新增 conversation_history
└── scripts/
    └── generate_credit_data.py     ← B2 新增（生成模拟数据）
```

## 改造步骤总览

详见 `_改造计划/任务清单.md`，按顺序执行：

```
B1 建表SQL → B2 生成数据 → B3 改元数据
    ↓ 重建数据库 + 重建索引 + 验证基础查询
B4 clarify_query节点 → B5 rewrite_query节点 → B6 更新prompt
    ↓
B7 跑30个测试用例 → 根据失败迭代meta_config
```

## 新增节点说明

### clarify_query（B4 新增）

插在 `add_extra_context` 和 `generate_sql` 之间。

**作用**：检测歧义指标（如"逾期率"可以是首逾率或在贷逾期率），追问用户澄清口径。

**触发条件**：query 涉及歧义指标 AND 用户没有提供澄清词（首逾/M1/M2/在贷）。

**state 新增字段**：`clarification_question: str | None`

**图的条件边**：
- `clarification_question is not None` → 返回追问，END
- `clarification_question is None` → 继续 `generate_sql`

### rewrite_query（B5 新增）

插在 `START` 和 `extract_keywords` 之间（第一步）。

**作用**：把多轮对话中含指代的问题改写成完整、自包含的问题。

**state 新增字段**：`conversation_history: list[dict]`

**API 新增字段**：`query_schema.py` 里加 `conversation_history: list[dict] = []`

## 注意事项

- 每完成一个步骤，在 `_改造计划/任务清单.md` 里打勾
- B1-B3 完成后必须验证基础查询跑通，再做 B4-B5
- 修改 `state.py` 时先加字段，再改节点，再改 graph，顺序不能反
- `meta_config.yaml` 的描述质量直接决定召回准确率，多写 alias 和 examples
