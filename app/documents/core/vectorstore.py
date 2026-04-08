from langchain_qdrant import QdrantVectorStore
from loguru import logger
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams

import env

from .embedding import get_embeddings_model

client = QdrantClient(url=env.QDRANT_URL, api_key=env.QDRANT_API_KEY)
collection_name = "user_documents"


async def init_vector_store():
    try:
        if not client.collection_exists(collection_name=collection_name):
            logger.info(f"Đang tạo mới Qdrant collection: {collection_name}")
            client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(size=768, distance=Distance.COSINE),
            )
            logger.info("✅ Tạo Qdrant collection thành công!")
        else:
            logger.info(f"✅ Qdrant collection '{collection_name}' đã sẵn sàng.")
    except Exception as e:
        logger.error(f"❌ Lỗi khi khởi tạo vector store: {e}")


def get_vector_store():
    return QdrantVectorStore(
        client=client,
        collection_name=collection_name,
        embedding=get_embeddings_model(),
    )


def add_documents_to_store(texts, metadatas):
    vector_store = get_vector_store()
    vector_store.add_texts(texts=texts, metadatas=metadatas)
