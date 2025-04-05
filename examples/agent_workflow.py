from llama_index.core.agent.workflow import AgentWorkflow

from .custom_llm import CozeLLM
from .tools import execute_api_call, get_now_local_datetime

llm = CozeLLM()


workflow = AgentWorkflow.from_tools_or_functions(
    [execute_api_call, get_now_local_datetime],
    llm=llm,
    system_prompt="You are an agent that can perform basic mathematical operations using tools.",
)


async def main():
    # response = await workflow.run(user_msg="获取当前所有传感器信息,")
    await workflow.run(user_msg="获取最近30天的浇水记录")
    # print(response)


if __name__ == "__main__":
    from .coze_llm import __name__ as coze_name
    from .custom_llm import __name__ as cus_name
    from .utils import set_debug

    set_debug(coze_name, cus_name)

    import asyncio

    asyncio.run(main())
