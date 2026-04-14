from pydantic import BaseModel

class UploadResponse(BaseModel):
    filename: str
    size_mb: float
    content_type: str