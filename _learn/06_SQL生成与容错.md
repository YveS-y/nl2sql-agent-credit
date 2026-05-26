# 第 6 课自测：SQL 生成与容错

**涉及文件**：`app/agent/nodes/generate_sql.py` · `validate_sql.py` · `correct_sql.py` · `execute_sql.py` · `app/agent/graph.py`

---

## ⚡ 实战任务

打开 `app/agent/graph.py`，找到 `validate_sql` 后的条件边，把路由函数的名字和它的两个返回值写下来（分别对应「去 correct」和「去 execute」的字符串是什么）。

然后打开 `correct_sql.py`，确认一件事：这个节点有没有重试循环？如果有，最多几次；如果没有，代码里用什么方式保证「只跑一次」？

最后回答：`validate_sql` 用 `EXPLAIN` 而不是直接执行 SQL，这个选择防的是什么具体问题？

→ 预期：能说出路由函数名 + 两个返回值字符串；能说出 correct 的执行次数和保证方式；能说出 EXPLAIN 防的具体风险（不是「副作用」，是什么副作用）。
