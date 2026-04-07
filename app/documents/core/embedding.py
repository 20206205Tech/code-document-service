import torch
from langchain_huggingface import HuggingFaceEmbeddings
from loguru import logger

# Xác định thiết bị chạy
if torch.cuda.is_available():
    current_device = "cuda"
elif torch.backends.mps.is_available():
    current_device = "mps"
else:
    current_device = "cpu"

# Khởi tạo Model Embedding
embeddings_model = HuggingFaceEmbeddings(
    model_name="keepitreal/vietnamese-sbert",
    model_kwargs={"device": current_device},
    encode_kwargs={"normalize_embeddings": True},
)

logger.info(f"✅ Embedding Model loaded on: {current_device}")
