from fastapi import APIRouter, BackgroundTasks, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user_id
from common.response.base_response import BaseResponse
from database.config import get_db

from . import schema, service

router = APIRouter(prefix="/documents", tags=["Documents"])


@router.post("/upload", response_model=BaseResponse[schema.DocumentUploadResponse])
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(..., description="Document file to upload"),
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    data = service.handle_document_upload(db, background_tasks, file, user_id)

    return BaseResponse(
        success=True,
        message="Tải lên thành công. Đang xử lý tài liệu trong nền.",
        data=data,
    )


@router.get("/{doc_id}", response_model=BaseResponse[schema.DocumentDetailResponse])
def get_document_status(
    doc_id: str,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    doc = service.get_document_by_id(db, doc_id, user_id)

    if not doc:
        raise HTTPException(status_code=404, detail="Không tìm thấy tài liệu")

    return BaseResponse(
        success=True,
        message="Lấy thông tin tài liệu thành công",
        data=schema.DocumentDetailResponse.model_validate(doc),
    )


@router.get("/", response_model=BaseResponse)
def list_user_documents(
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 20,
):
    docs, total = service.get_user_documents_list(db, user_id, skip, limit)

    doc_list = [
        {
            "id": str(doc.id),
            "filename": doc.filename,
            "status": doc.status,
            "created_at": doc.created_at,
            "updated_at": doc.updated_at,
        }
        for doc in docs
    ]

    return BaseResponse(
        success=True,
        message=f"Đã lấy {len(doc_list)} tài liệu",
        data={"documents": doc_list, "total": total, "skip": skip, "limit": limit},
    )


@router.post("/{doc_id}/retry")
async def retry_document_processing(
    doc_id: str,
    background_tasks: BackgroundTasks,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    doc = service.retry_processing(db, background_tasks, doc_id, user_id)

    if not doc:
        raise HTTPException(status_code=404, detail="Không tìm thấy tài liệu")

    return BaseResponse(
        success=True,
        message="Đã đưa tài liệu vào hàng chờ xử lý lại",
        data={"doc_id": doc_id},
    )
