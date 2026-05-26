# 第 3 课自测：LangGraph 状态机

**涉及文件**：`app/agent/state.py` · `app/agent/context.py` · `app/agent/graph.py`

---

## ⚡ 实战任务

打开 `app/agent/state.py`，把 State 里所有字段名列出来（不需要类型，只要名字）。再打开 `app/agent/context.py`，同样列出 Context 里的字段名。

然后回答这个具体问题：`column_qdrant_repository` 放在 Context 里而不是 State 里，**不是因为「设计风格」**，而是有一个具体的技术原因——是什么？

→ 预期：能列出两个文件的字段名；能说出 repository 不能放进 State 的技术原因（不是「应该」，是「不能」）。
