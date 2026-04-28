from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from app.pydanticModels import UploadResponse, AuthenticatedUser
from app.services.extractor import extract
from app.services.chunker import chunk_text
from app.services.embedder import generate_embeddings
from app.services.supabaseStore import store_chunks, store_document
from app.services.authService import get_current_user

router = APIRouter()

ALLOWED_TYPES = ["application/pdf", "text/plain"]
MAX_SIZE_MB = 10

@router.post("/upload", response_model=UploadResponse)
async def upload_file(
    file: UploadFile = File(...),
    current_user: AuthenticatedUser = Depends(get_current_user),
):

    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=400, detail="Only PDF and TXT files allowed")
    
    content = await file.read()

    print(f"Content type received: '{file.content_type}'")

    size_mb = len(content) / (1024 * 1024)
    if size_mb > MAX_SIZE_MB:
        raise HTTPException(status_code=400, detail=f"File too large. Max size is {MAX_SIZE_MB}MB")
    
    # Text Extraction
    try:
        extraction = extract(content, file.content_type)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    full_text = "\n".join(extraction.pages) # Combine all page texts into one string

    # Creating Chunks
    chunks = chunk_text(full_text)

    # Embedding Generation
    embeddings = generate_embeddings(chunks)

    document_id = store_document(
        owner_id=str(current_user.id),
        filename=file.filename,
        content_type=file.content_type,
        total_pages=extraction.total_pages
    )

    store_chunks(
        document_id=document_id,
        chunks=chunks,
        embeddings=embeddings,
    )

    return UploadResponse(
        filename=file.filename,
        size_mb=size_mb,
        content_type=file.content_type,
        total_pages=extraction.total_pages
    )