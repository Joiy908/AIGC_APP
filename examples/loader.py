from llama_index.core import SimpleDirectoryReader
from llama_index.core.node_parser import MarkdownNodeParser

docs = SimpleDirectoryReader(input_dir="./data").load_data()


parser = MarkdownNodeParser()
nodes = parser.get_nodes_from_documents(docs)

