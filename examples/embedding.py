# from sentence_transformers import SentenceTransformer

# model = SentenceTransformer("./text2vec-base-chinese")
# embeddings = model.encode([
#     "The weather is lovely today.",
#     "It's so sunny outside!",
#     "He drove to the stadium.",
# ])

from llama_index.embeddings.huggingface import HuggingFaceEmbedding

embed_model = HuggingFaceEmbedding(model_name="./embedding_models/text2vec-base-chinese")
embeddings = embed_model.get_text_embedding("Hello World!")
print(len(embeddings))
print(embeddings[:5])


