from contextvars import ContextVar

'''
【contextvars.ContextVar】请求级别的全局变量，同一个变量在不同请求中值不同，互不干扰
├─ 核心能力
│   并发安全：多个请求同时读写同一个 ContextVar，各自拿到各自的值
├─ 在本项目中的角色
│   在整个请求链路中传递 request_id，让每条日志都能关联到具体请求
└─ 使用的 API
    ├─ ContextVar("name", default=...) → 创建变量实例（全局只有这一个）
    ├─ .set(value)   → 中间件里设置当前请求的值
    └─ .get()        → 任何地方读取，自动返回当前请求的值
'''

request_id_ctx_var = ContextVar("request_id", default="1")

