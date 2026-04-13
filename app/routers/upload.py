from fastapi import APIRouter, UploadFile, File, HTTPException
from app.schemas import UploadResponse

router = APIRouter()

ALLOWED_TYPES = ["application/pdf", "text/plain"]
MAX_SIZE_MB = 100

@router.post("/upload", response_model=UploadResponse)
async def upload_file(file: UploadFile = File(...)):

    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=400, detail="Only PDF and TXT files allowed")
    
    contents = await file.read()

    size_mb = len(contents) / (1024 * 1024)
    if size_mb > MAX_SIZE_MB:
        raise HTTPException(status_code=400, detail=f"File too large. Max size is {MAX_SIZE_MB}MB")

    return {"filename": file.filename, "size_mb": round(size_mb, 2), "type": file.content_type}