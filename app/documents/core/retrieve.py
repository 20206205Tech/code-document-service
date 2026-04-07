# from loguru import logger
# from .vectorstore import get_vector_store

# def retrieve_context(query: str, user_id: str, doc_id: str = None, top_k: int = 5):
#     try:
#         vector_store = get_vector_store()

#         # Filter để chỉ tìm trong tài liệu của User hoặc đúng DocID đó
#         filter_dict = {"user_id": user_id}
#         if doc_id:
#             filter_dict["doc_id"] = doc_id

#         search_results = vector_store.similarity_search(
#             query,
#             k=top_k,
#             filter=filter_dict
#         )

#         context = "\n\n".join([doc.page_content for doc in search_results])
#         return context
#     except Exception as e:
#         logger.error(f"❌ Lỗi khi truy vấn vector store: {e}")
#         return ""
