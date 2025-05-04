# from sentence_transformers import SentenceTransformer

# model = SentenceTransformer("./text2vec-base-chinese")
# embeddings = model.encode([
#     "The weather is lovely today.",
#     "It's so sunny outside!",
#     "He drove to the stadium.",
# ])

# from llama_index.embeddings.huggingface import HuggingFaceEmbedding

# embed_model = HuggingFaceEmbedding(model_name="./embedding_models/text2vec-base-chinese")
# embeddings = embed_model.get_text_embedding("Hello World!")
# print(len(embeddings))
# print(embeddings[:5])

# custom embedding
from typing import Any

import grpc
from llama_index.core.embeddings import BaseEmbedding
from pydantic import PrivateAttr

from grpc_embedding import get_embedding_pb2, get_embedding_pb2_grpc


class CustomEmbedding(BaseEmbedding):
    _channel: grpc.Channel = PrivateAttr()
    _stub: get_embedding_pb2_grpc.EmbeddingServiceStub = PrivateAttr()
    def __init__(
        self,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self._channel = grpc.insecure_channel('localhost:50051')
        self._stub = get_embedding_pb2_grpc.EmbeddingServiceStub(self._channel)

    def _get_embedding(self, text: str) -> list[float]:
        request = get_embedding_pb2.TextRequest(text=text)
        try:
            # 发起请求
            response = self._stub.GetTextEmbedding(request)
            return response.embedding
        except grpc.RpcError as e:
            print(f"RPC failed: {e.code()} - {e.details()}")
            return []

    def _get_query_embedding(self, query: str) -> list[float]:
        return self._get_embedding(query)

    def _get_text_embedding(self, text: str) -> list[float]:
        return self._get_embedding(text)

    def _get_text_embeddings(self, texts: list[str]) -> list[list[float]]:
        return [self._get_embedding(s) for s in texts]

    async def _aget_query_embedding(self, query: str) -> list[float]:
        return self._get_query_embedding(query)

    async def _aget_text_embedding(self, text: str) -> list[float]:
        return self._get_text_embedding(text)


if __name__ == '__main__':
    x = CustomEmbedding()
    print(x.get_query_embedding('sss'))

