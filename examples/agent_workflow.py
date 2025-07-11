from llama_index.core import Settings
from llama_index.core.agent.workflow import ReActAgent
from llama_index.core.agent.workflow.workflow_events import (
    AgentInput,
    AgentOutput,
    AgentStream,
    ToolCall,
    ToolCallResult,
)
from llama_index.core.base.llms.types import TextBlock
from llama_index.core.schema import NodeWithScore
from llama_index.core.tools import FunctionTool, QueryEngineTool

from .custom_llm import CozeLLM
from .tools import execute_api_call, get_grape_docs, get_now_local_datetime
from .utils import Colors

llm = CozeLLM()
Settings.llm = llm

docs_tool = FunctionTool.from_defaults(get_grape_docs)


api_tool = FunctionTool.from_defaults(execute_api_call)
datetime_tool = FunctionTool.from_defaults(get_now_local_datetime)

agent = ReActAgent(
    name="grape_agent",
    description="An agent that can query knowledge about grape cultivation and view data from vineyard areas.",
    tools=[docs_tool, api_tool, datetime_tool],
)


async def main():
    handler = agent.run(user_msg="葡萄有黑点怎么办？")
    async for ev in handler.stream_events():
        match ev:
            case AgentInput():
                print(Colors.USER_PROMPT, end="")
                for msg in ev.input:
                    # print(msg.content)
                    assert "blocks" in dir(msg)
                    for blk in msg.blocks:
                        assert isinstance(blk, TextBlock)
                        if isinstance(blk, TextBlock):
                            print(blk.text)
                print(Colors.RESET)
            case AgentStream():
                print(Colors.RESPONSE, end="", flush=True)
                print(ev.delta, end="", flush=True)
                print(Colors.RESET, end="", flush=True)
            case ToolCallResult():
                print(Colors.USER_PROMPT, end="")
                print(f"raw input: {ev.tool_output.raw_input}\nraw output: {ev.tool_output.raw_output}")
                print(Colors.RESET)
            # case ToolCall() | AgentOutput() | _:
            case _:
                continue

    await handler


if __name__ == "__main__":
    # from .coze_llm import __name__ as coze_name
    # from .custom_llm import __name__ as cus_name
    # from .utils import set_debug

    # set_debug(coze_name, cus_name)

    import asyncio

    asyncio.run(main())
