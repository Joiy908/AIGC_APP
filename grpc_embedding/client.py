import grpc

from grpc_embedding import get_embedding_pb2, get_embedding_pb2_grpc


def run():
    # 建立与 gRPC 服务器的连接
    channel = grpc.insecure_channel('localhost:50051')
    stub = get_embedding_pb2_grpc.EmbeddingServiceStub(channel)

    # 构造请求
    text = "这是一个测试句子。"
    request = get_embedding_pb2.TextRequest(text=text)

    try:
        # 发起请求
        response = stub.GetTextEmbedding(request)

        # 打印响应
        print(f"Embedding (length {len(response.embedding)}):")
        print(response.embedding)

    except grpc.RpcError as e:
        print(f"RPC failed: {e.code()} - {e.details()}")


if __name__ == '__main__':
    run()
