import os
from pathlib import Path
from typing import Optional

from loguru import logger
from sqlalchemy.orm import Session

from app.documents.core.chunking import chunk_text
from app.documents.core.vectorstore import add_documents_to_store
from app.documents.services.parser import document_parser
from app.documents.services.storage import r2_storage
from app.documents.services.summarizer import ai_summarizer
from database.config import SessionLocal
from database.models import Document


class DocumentProcessingError(Exception):
    pass


class DocumentProcessor:
    def __init__(self, db: Session):
        self.db = db

    def _update_document_status(
        self, doc: Document, status: str, error_message: Optional[str] = None
    ) -> None:
        doc.status = status
        if error_message and status == "FAILED":
            # You could add an error_message field to the Document model
            logger.error(f"Document {doc.id} failed: {error_message}")

        self.db.commit()
        logger.info(f"📝 Document {doc.id} status updated to: {status}")

    def _extract_file_key_from_url(self, file_url: str) -> str:
        if "/" in file_url:
            parts = file_url.split("/")
            # Get everything after the domain
            key = "/".join(parts[3:])
            return key
        return file_url

    def _cleanup_tempfile(self, temp_path: Optional[Path]) -> None:
        if temp_path and temp_path.exists():
            try:
                os.unlink(temp_path)
                logger.info(f"🗑️  Temporary file deleted: {temp_path}")
            except Exception as e:
                logger.warning(f"⚠️  Failed to delete temp file {temp_path}: {e}")

    def process(self, doc_id: str) -> bool:
        temp_file_path: Optional[Path] = None
        try:
            # 1. Lấy document từ DB
            doc = self.db.query(Document).filter(Document.id == doc_id).first()
            if not doc:
                logger.error(f"❌ Document {doc_id} not found")
                return False

            self._update_document_status(doc, "PROCESSING")

            # 2. Trích xuất text (nếu chưa có)
            if not doc.extracted_text:
                file_key = self._extract_file_key_from_url(doc.file_url)
                temp_file_path = r2_storage.download_to_tempfile(file_key)
                extracted_text = document_parser.parse_document(temp_file_path)
                doc.extracted_text = extracted_text
                self.db.commit()
            else:
                extracted_text = doc.extracted_text

            # 3. Tóm tắt nội dung
            summary = ai_summarizer.summarize(extracted_text)
            doc.summary = summary
            self.db.commit()

            # 4. Chia nhỏ (Chunking) - Sử dụng module mới
            chunks = chunk_text(extracted_text)

            # 5. Lưu vào Vector Store - Sử dụng module mới
            metadatas = [
                {
                    "user_id": str(doc.user_id),
                    "doc_id": str(doc.id),
                    "filename": doc.filename,
                }
                for _ in chunks
            ]
            add_documents_to_store(chunks, metadatas)

            self._update_document_status(doc, "COMPLETED")
            return True

        except Exception as e:
            logger.error(f"❌ Error: {str(e)}")
            if doc:
                self._update_document_status(doc, "FAILED", str(e))
            return False
        finally:
            self._cleanup_tempfile(temp_file_path)


def process_document_task(doc_id: str) -> None:
    logger.info(f"🚀 Background task started for document: {doc_id}")

    db = SessionLocal()

    try:
        processor = DocumentProcessor(db)
        success = processor.process(doc_id)

        if success:
            logger.info(f"✅ Background task completed successfully for: {doc_id}")
        else:
            logger.error(f"❌ Background task failed for: {doc_id}")

    except Exception:
        logger.exception(f"❌ Fatal error in background task for {doc_id}")

    finally:
        db.close()
        logger.info(f"🔒 Database session closed for document: {doc_id}")
