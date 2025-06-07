import time
from concurrent import futures

import grpc
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

from grpc_embedding import get_embedding_pb2, get_embedding_pb2_grpc


class EmbeddingServiceServicer(get_embedding_pb2_grpc.EmbeddingServiceServicer):
    def __init__(self):
        self.embed_model = HuggingFaceEmbedding(
            model_name="./embedding_models/text2vec-base-chinese"
        )

    def GetTextEmbedding(self, request, context):
        try:
            # 调用嵌入模型获取向量
            embedding = self.embed_model.get_text_embedding(request.text)
            return get_embedding_pb2.EmbeddingResponse(embedding=embedding)
        except Exception as e:
            context.set_details(str(e))
            context.set_code(grpc.StatusCode.INTERNAL)
            return get_embedding_pb2.EmbeddingResponse()


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    get_embedding_pb2_grpc.add_EmbeddingServiceServicer_to_server(
        EmbeddingServiceServicer(), server
    )

    server.add_insecure_port('[::]:50051')
    server.start()
    print("✅ gRPC server started at port 50051...")
    try:
        while True:
            time.sleep(86400)  # 保持运行
    except KeyboardInterrupt:
        print("❌ Shutting down server...")
        server.stop(0)


if __name__ == '__main__':
    serve()
