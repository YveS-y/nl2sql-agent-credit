import httpx
from langchain.chat_models import init_chat_model
from langchain_openai import ChatOpenAI

from app.conf.app_config import app_config

if app_config.llm.bypass_proxy:
    # 方案B：绕过系统代理直连（dashscope 是国内地址，不需要走代理）
    # trust_env=False 告诉 httpx 忽略系统的代理环境变量
    llm = ChatOpenAI(
        model=app_config.llm.model_name,
        api_key=app_config.llm.api_key,
        base_url=app_config.llm.base_url,
        temperature=0,
        model_kwargs={"extra_body": {"enable_thinking": False}},
        http_client=httpx.Client(trust_env=False),
        http_async_client=httpx.AsyncClient(trust_env=False),
    )
else:
    # 方案A：走系统代理（适合 base_url 需要翻墙的情况）
    llm = init_chat_model(
        model=app_config.llm.model_name,
        model_provider="openai",
        api_key=app_config.llm.api_key,
        base_url=app_config.llm.base_url,
        temperature=0,
    )


if __name__ == '__main__':
    for chunk in llm.stream("What is the meaning of life?"):
        print(chunk.text)
