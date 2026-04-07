from fastapi import APIRouter

from app.documents.api.router import router as doc_router

index_router = APIRouter()

index_router.include_router(doc_router)
