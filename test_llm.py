import asyncio, time
from app.agent.llm import llm

async def test():
    start = time.time()
    result = await llm.ainvoke("你好，回复ok两个字")
    print("耗时:", round(time.time()-start, 2), "秒")
    print("回复:", result.content)

asyncio.run(test())
