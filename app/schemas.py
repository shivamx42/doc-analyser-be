from pydantic import BaseModel

class UploadResponse(BaseModel):
    filename: str
    size_mb: float
    type: str