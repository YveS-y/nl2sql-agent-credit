# 第 7 课自测：流式响应与 SSE

**涉及文件**：`app/services/query_service.py` · `app/agent/nodes/execute_sql.py`（或其他有 writer 调用的节点）

---

## ⚡ 实战任务

打开 `app/services/query_service.py`，找到 `astream` 的调用，把 `stream_mode` 参数的具体值抄下来。

然后在节点文件里找到 `writer` 的 push 调用（在哪个节点，push 了什么），把那一行代码完整抄下来。

最后回答：为什么用 `stream_mode="custom"` 而不是 `"values"`？用「前端会收到什么」来解释，不要用「最佳实践」。

→ 预期：能说出 stream_mode 的具体值；能找到 writer.push 所在节点和完整的那行代码；能用「前端会收到 X 而不是 Y」解释 custom vs values 的区别。
