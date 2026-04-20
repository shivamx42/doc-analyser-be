from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime

class UploadResponse(BaseModel):
    filename: str
    size_mb: float
    content_type: str
    total_pages: int

class QueryRequest(BaseModel):
    question: str
    document_id: Optional[UUID] = None

class ChunkResult(BaseModel):
    id: UUID
    document_id: UUID
    content: str
    similarity: float

class QueryResponse(BaseModel):
    question: str
    answer: str
    results: list[ChunkResult]

# model to send data to backend when user tries to register
class RegisterRequest(BaseModel):
    email: str
    password: str
    display_name: str

# model to send data back to frontend after registration
class RegisterResponse(BaseModel):
    user_id: UUID
    email: str
    display_name: str
    message: str

class DocumentListItem(BaseModel):
    id: UUID
    filename: str
    content_type: str
    total_pages: int
    created_at: datetime

class DocumentListResponse(BaseModel):
    documents: list[DocumentListItem]

class AuthenticatedUser(BaseModel):
    id: UUID
    email: Optional[str] = None