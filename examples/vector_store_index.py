from llama_index.core import VectorStoreIndex
from llama_index.core.retrievers import VectorIndexRetriever

from .loader import nodes

index = VectorStoreIndex(nodes)

# retriever = index.as_retriever()
# nodes = retriever.retrieve("葡萄白粉病")
# configure retriever
retriever = VectorIndexRetriever(
    index=index,
    similarity_top_k=3,
)


# nodes = retriever.retrieve("什么时候浇水")
