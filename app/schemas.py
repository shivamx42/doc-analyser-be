from pydantic import BaseModel
from typing import Optional
from uuid import UUID

class UploadResponse(BaseModel):
    filename: str
    size_mb: float
    content_type: str
    total_pages: int

class QueryRequest(BaseModel):
    question: str
    document_id: Optional[str] = None

class ChunkResult(BaseModel):
    id: UUID
    document_id: UUID
    content: str
    similarity: float

class QueryResponse(BaseModel):
    question: str
    answer: str
    results: list[ChunkResult]