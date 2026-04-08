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

    model_config = ConfigDict(from_attributes=True)


class DocumentDetailResponse(BaseModel):
    id: UUID = Field(..., description="Unique document ID")
    filename: str = Field(..., description="Original filename")
    status: str = Field(..., description="Current processing status")

    has_file: bool = Field(default=False, description="Trạng thái tồn tại của file gốc")
    has_content: bool = Field(
        default=False, description="Trạng thái tồn tại của file nội dung (.md)"
    )
    has_summary: bool = Field(
        default=False, description="Trạng thái tồn tại của file tóm tắt (.txt)"
    )

    file_url: Optional[str] = Field(None, description="URL to access the file")
    parsed_content_url: Optional[str] = Field(
        None, description="URL to access the parsed markdown file"
    )
    summary_url: Optional[str] = Field(
        None, description="URL to access the summary text file"
    )

    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    model_config = ConfigDict(from_attributes=True)


class DocumentListItem(BaseModel):
    id: UUID = Field(..., description="Unique document ID")
    filename: str
    status: str

    has_file: bool
    has_content: bool
    has_summary: bool

    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DocumentListResponse(BaseModel):
    documents: List[DocumentListItem]
    total: int = Field(..., description="Total number of documents")
    skip: int = Field(..., description="Number of records skipped")
    limit: int = Field(..., description="Maximum records returned")

    model_config = ConfigDict(from_attributes=True)
