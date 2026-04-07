from datetime import datetime
from enum import Enum
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class DocumentStatusEnum(str, Enum):
    UPLOADED = "UPLOADED"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class DocumentUploadResponse(BaseModel):
    doc_id: UUID = Field(..., description="Unique document ID")
    filename: str = Field(..., description="Original filename")
    status: str = Field(..., description="Current processing status")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "doc_id": "123e4567-e89b-12d3-a456-426614174000",
                "filename": "report.pdf",
                "status": "UPLOADED",
            }
        },
    )


class DocumentDetailResponse(BaseModel):
    id: UUID = Field(..., description="Unique document ID")
    filename: str = Field(..., description="Original filename")
    status: str = Field(..., description="Current processing status")
    file_url: Optional[str] = Field(None, description="URL to access the file")
    extracted_text: Optional[str] = Field(None, description="Extracted text content")
    summary: Optional[str] = Field(None, description="AI-generated summary")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "filename": "report.pdf",
                "status": "COMPLETED",
                "file_url": "https://pub-xxx.r2.dev/user123/report.pdf",
                "extracted_text": "Full document text...",
                "summary": "This document discusses...",
                "created_at": "2024-04-07T10:00:00Z",
                "updated_at": "2024-04-07T10:05:00Z",
            }
        },
    )


class DocumentListItem(BaseModel):
    id: UUID = Field(..., description="Unique document ID")
    filename: str
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DocumentListResponse(BaseModel):
    documents: List[DocumentListItem]
    total: int = Field(..., description="Total number of documents")
    skip: int = Field(..., description="Number of records skipped")
    limit: int = Field(..., description="Maximum records returned")

    model_config = ConfigDict(from_attributes=True)
