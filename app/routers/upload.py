from fastapi import APIRouter, UploadFile, File, HTTPException
from torch import chunk
from app.schemas import UploadResponse
from app.services.extractor import extract
from app.services.chunker import chunk_text

router = APIRouter()

ALLOWED_TYPES = ["application/pdf", "text/plain"]
MAX_SIZE_MB = 100

@router.post("/upload", response_model=UploadResponse)
async def upload_file(file: UploadFile = File(...)):

    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=400, detail="Only PDF and TXT files allowed")
    
    content = await file.read()

    print(f"Content type received: '{file.content_type}'")

    size_mb = len(content) / (1024 * 1024)
    if size_mb > MAX_SIZE_MB:
        raise HTTPException(status_code=400, detail=f"File too large. Max size is {MAX_SIZE_MB}MB")
    
    extraction = extract(content, file.content_type)
    full_text = "\n".join(page.text for page in extraction.pages) # Combine all page texts into one string
    chunks = chunk_text(full_text)

    # print(chunks)

    return UploadResponse(
        filename=file.filename,
        size_mb=size_mb,
        content_type=file.content_type,
    )