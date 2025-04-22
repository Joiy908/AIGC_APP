from llama_index.core import VectorStoreIndex

from .custom_llm import CozeLLM
from .loader import nodes

llm = CozeLLM()

index = VectorStoreIndex(nodes)

agent = index.as_query_engine(llm=llm, streaming=True)

if __name__ == "__main__":
    from .coze_llm import __name__ as coze_name
    from .custom_llm import __name__ as cus_name
    from .utils import set_debug

    set_debug(coze_name, cus_name)
    streaming_res = agent.query("葡萄浇水计划")
    # streaming_res.print_response_stream()
