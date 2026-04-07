from langchain_text_splitters import RecursiveCharacterTextSplitter
from loguru import logger


def chunk_text(text: str, chunk_size: int = 1000, chunk_overlap: int = 100):
    try:
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", ".", " ", ""],
        )
        chunks = text_splitter.split_text(text)
        logger.info(f"✂️ Đã chia văn bản thành {len(chunks)} đoạn (chunks).")
        return chunks
    except Exception as e:
        logger.error(f"❌ Lỗi khi chunking văn bản: {e}")
        return [text]
