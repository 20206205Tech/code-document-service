import uuid

from fastapi import BackgroundTasks, HTTPException, UploadFile, status
from loguru import logger
from sqlalchemy.orm import Session

from app.documents.services.storage import R2StorageError, r2_storage
from app.documents.tasks.worker import process_document_task
from database.models import Document
from utils.file_validation import validate_upload_file

from . import schema


def handle_document_upload(
    db: Session, background_tasks: BackgroundTasks, file: UploadFile, user_id: str
):
    try:
        filename, extension = validate_upload_file(file)
        logger.info(f"📤 Đang xử lý upload cho user {user_id}: {filename}")

        # Tạo một tên file duy nhất: user_id/uuid_filename.pdf
        unique_id = uuid.uuid4().hex
        file_key = f"{user_id}/{unique_id}_{filename}"

        # file_key = f"{user_id}/{filename}"
        try:
            file_url = r2_storage.upload_file(
                file_obj=file.file, file_key=file_key, content_type=file.content_type
            )
        except R2StorageError as e:
            logger.error(f"❌ R2 upload failed: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to upload file to storage: {str(e)}",
            )

        # 3. CREATE DATABASE RECORD
        new_doc = Document(
            user_id=user_id,
            filename=filename,
            file_url=file_url,
            status=schema.DocumentStatusEnum.UPLOADED.value,
        )
        db.add(new_doc)
        db.commit()
        db.refresh(new_doc)
        logger.info(f"✅ Đã tạo bản ghi document: {new_doc.id}")

        # 4. TRIGGER BACKGROUND PROCESSING
        background_tasks.add_task(process_document_task, str(new_doc.id))
        logger.info(f"🚀 Đã đưa task vào hàng chờ xử lý: {new_doc.id}")

        return schema.DocumentUploadResponse(
            doc_id=str(new_doc.id), filename=filename, status=new_doc.status
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"❌ Lỗi không xác định khi upload")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}",
        )


def get_document_by_id(db: Session, doc_id: str, user_id: str):
    # 1. Lấy thông tin từ DB
    doc = (
        db.query(Document)
        .filter(Document.id == doc_id, Document.user_id == user_id)
        .first()
    )

    if not doc:
        return None

    # 2. Lấy file_key từ file_url đã lưu
    # doc.file_url hiện đang có dạng: https://domain.com/user_id/uuid_filename.pdf
    try:
        # Cách an toàn để lấy key từ URL:
        from urllib.parse import urlparse

        path = urlparse(doc.file_url).path  # Kết quả: /user_id/uuid_filename.pdf
        file_key = path.lstrip("/")  # Kết quả: user_id/uuid_filename.pdf

        presigned_url = r2_storage.generate_presigned_url(file_key, expiration=3600)
        doc.file_url = presigned_url
    except Exception as e:
        logger.error(f"⚠️ Không thể tạo presigned URL: {e}")

    return doc


def get_user_documents_list(db: Session, user_id: str, skip: int = 0, limit: int = 20):
    documents = (
        db.query(Document)
        .filter(Document.user_id == user_id)
        .order_by(Document.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    total = db.query(Document).filter(Document.user_id == user_id).count()
    return documents, total


def retry_processing(
    db: Session, background_tasks: BackgroundTasks, doc_id: str, user_id: str
):
    doc = get_document_by_id(db, doc_id, user_id)
    if not doc:
        return None

    doc.status = schema.DocumentStatusEnum.UPLOADED.value
    db.commit()
    background_tasks.add_task(process_document_task, str(doc.id))
    return doc
