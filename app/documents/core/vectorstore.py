from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient

import env

from .embedding import embeddings_model

client = QdrantClient(url=env.QDRANT_URL, api_key=env.QDRANT_API_KEY)
collection_name = "user_documents"


def get_vector_store():
    return QdrantVectorStore(
        client=client,
        collection_name=collection_name,
        embedding=embeddings_model,
    )


def add_documents_to_store(texts, metadatas):
    vector_store = get_vector_store()
    vector_store.add_texts(texts=texts, metadatas=metadatas)
