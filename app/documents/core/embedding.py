import torch
from langchain_huggingface import HuggingFaceEmbeddings
from loguru import logger

_embeddings_model = None


def get_embeddings_model():
    global _embeddings_model

    if _embeddings_model is None:
        logger.info("⏳ Đang khởi tạo Embedding Model (quá trình này chỉ chạy 1 lần)...")

        if torch.cuda.is_available():
            current_device = "cuda"
        elif torch.backends.mps.is_available():
            current_device = "mps"
        else:
            current_device = "cpu"

        _embeddings_model = HuggingFaceEmbeddings(
            model_name="keepitreal/vietnamese-sbert",
            model_kwargs={"device": current_device},
            encode_kwargs={"normalize_embeddings": True},
        )

        logger.info(f"✅ Embedding Model loaded on: {current_device}")

    return _embeddings_model
