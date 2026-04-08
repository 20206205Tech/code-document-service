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

        new_doc = Document(
            user_id=user_id,
            filename=filename,
            status=schema.DocumentStatusEnum.UPLOADED.value,
            has_file=False,
        )
        db.add(new_doc)
        db.commit()
        db.refresh(new_doc)

        # 2. Định nghĩa Key theo quy ước mới
        doc_uuid = str(new_doc.id)
        file_key = f"{user_id}/document/{doc_uuid}"

        # 3. Upload lên R2
        try:
            r2_storage.upload_file(
                file_obj=file.file, file_key=file_key, content_type=file.content_type
            )
            # Cập nhật cờ đã có file
            new_doc.has_file = True
            db.commit()
        except R2StorageError as e:
            logger.error(f"Lỗi khi upload lên R2: {e}")

        # 4. Đẩy vào Background Task
        background_tasks.add_task(process_document_task, doc_uuid)

        # Trả về response đúng định dạng thay vì dấu ...
        return schema.DocumentUploadResponse(
            doc_id=new_doc.id, filename=new_doc.filename, status=new_doc.status
        )

    except Exception as e:
        logger.exception(f"❌ Lỗi không xác định khi upload")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}",
        )


def get_document_by_id(db: Session, doc_id: str, user_id: str):
    doc = (
        db.query(Document)
        .filter(Document.id == doc_id, Document.user_id == user_id)
        .first()
    )

    if not doc:
        return None

    # Tạm thời gán thuộc tính để trả về API (các trường này phải có trong file schema.py)
    doc.file_url = None
    doc.parsed_content_url = None
    doc.summary_url = None

    try:
        if doc.has_file:
            doc_key = f"{user_id}/document/{doc.id}"
            doc.file_url = r2_storage.generate_presigned_url(doc_key)

        if doc.has_content:
            content_key = f"{user_id}/content/{doc.id}"
            doc.parsed_content_url = r2_storage.generate_presigned_url(content_key)

        if doc.has_summary:
            summary_key = f"{user_id}/summary/{doc.id}"
            doc.summary_url = r2_storage.generate_presigned_url(summary_key)

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
