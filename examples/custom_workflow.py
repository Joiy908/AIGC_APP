from typing import Literal

from llama_index.core import Settings
from llama_index.core.tools import FunctionTool, QueryEngineTool, ToolMetadata
from pydantic import BaseModel

from .custom_llm import CozeLLM
from .custom_reactagent import ReActAgent, StopSignal, StreamEvent, ToolCallResultMessage
from .tools import execute_api_call, get_now_local_datetime, get_grape_docs
from .utils import Colors

llm = CozeLLM()
Settings.llm = llm


docs_tool = FunctionTool.from_defaults(get_grape_docs)


api_tool = FunctionTool.from_defaults(execute_api_call)
datetime_tool = FunctionTool.from_defaults(get_now_local_datetime)

agent = ReActAgent(
    llm=llm,
    # name="grape_agent",
    # description="An agent that can query knowledge about grape cultivation and view data from vineyard areas.",
    tools=[docs_tool, api_tool, datetime_tool],
    timeout=2 * 60,
)


async def main():
    handler = agent.run(input="葡萄有黑点怎么办？")
    async for ev in handler.stream_events():
        # print(repr(ev))
        match ev:
            # case InputEvent():
            #     print(Colors.USER_PROMPT, end="")
            #     for msg in ev.input:
            #         # print(msg.content)
            #         assert "blocks" in dir(msg)
            #         for blk in msg.blocks:
            #             assert isinstance(blk, TextBlock)
            #             if isinstance(blk, TextBlock):
            #                 print(blk.text)
            #     print(Colors.RESET)
            case StreamEvent():
                print(Colors.RESPONSE, end="", flush=True)
                print(ev.delta, end="", flush=True)
                print(Colors.RESET, end="", flush=True)
            case ToolCallResultMessage():
                print(Colors.BLUE, end="", flush=True)
                print()
                print(ev.output, end="", flush=True)
                print()
                print(Colors.RESET, end="", flush=True)
            case StopSignal():
                print("\n === end ===")
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
