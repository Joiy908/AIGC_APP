from llama_index.core import Settings
from llama_index.core.agent.workflow import ReActAgent
from llama_index.core.schema import NodeWithScore
from llama_index.core.tools import FunctionTool, QueryEngineTool

from .custom_llm import CozeLLM
from .index_as_query_engine import index as grape_index
from .tools import execute_api_call, get_now_local_datetime
from .vector_store_index import retriever as grape_retriever

llm = CozeLLM()
Settings.llm = llm

grape_query_engine = grape_index.as_query_engine()

# docs_tool = QueryEngineTool(
#     query_engine=grape_query_engine,
#     metadata=ToolMetadata(
#         name="grape_query_engine",
#         description="Provide knowledges about grape",
#     ),
# )


def get_grape_docs(query: str) -> list[NodeWithScore]:
    """Get grape docs."""
    return grape_retriever.retrieve(query)


docs_tool = FunctionTool.from_defaults(get_grape_docs)


api_tool = FunctionTool.from_defaults(execute_api_call)
datetime_tool = FunctionTool.from_defaults(get_now_local_datetime)

agent = ReActAgent(
    name="grape_agent",
    description="An agent that can query knowledge about grape cultivation and view data from vineyard areas.",
    tools=[docs_tool, api_tool, datetime_tool],
)


async def main():
    ret = await agent.run(user_msg="葡萄有黑点怎么办？")
    print(ret)


if __name__ == "__main__":
    from .coze_llm import __name__ as coze_name
    from .custom_llm import __name__ as cus_name
    from .utils import set_debug

    set_debug(coze_name, cus_name)

    import asyncio

    asyncio.run(main())
