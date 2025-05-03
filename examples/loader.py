from llama_index.core import Settings, SimpleDirectoryReader
from llama_index.core.ingestion import IngestionPipeline
from llama_index.core.node_parser import MarkdownNodeParser
from .custom_embedding import CustomEmbeddings
# from llama_index.embeddings.huggingface import HuggingFaceEmbedding

# embed_model = HuggingFaceEmbedding(model_name="./embedding_models/text2vec-base-chinese")

embed_model = CustomEmbeddings()
Settings.embed_model = embed_model
docs = SimpleDirectoryReader(input_dir="./data").load_data()


pipeline = IngestionPipeline(
    transformations=[
        MarkdownNodeParser(),
        embed_model
    ],
)

pipeline.load('./cache/pipeline_storage')

nodes = pipeline.run(documents=docs, show_progress=True)
pipeline.persist("./cache/pipeline_storage")

