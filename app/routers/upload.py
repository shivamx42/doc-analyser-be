import os
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from app.pydanticModels import UploadResponse, AuthenticatedUser
from app.services.extractor import extract
from app.services.chunker import chunk_text
from app.services.embedder import generate_embeddings
from app.services.supabaseStore import store_chunks, store_document
from app.services.authService import get_current_user

router = APIRouter()

ALLOWED_TYPES = [
    "application/pdf", 
    "text/plain",
    "audio/mpeg",
    "audio/mp3",
    "audio/mp4",
    "audio/m4a",
    "audio/x-m4a",
    "audio/ogg",
    "audio/wav",
    "audio/x-wav",
    "audio/webm",
    "video/mp4",
    "video/webm",
    "audio/flac",
    "audio/x-flac"
]
MAX_SIZE_MB = 10

@router.post("/upload", response_model=UploadResponse)
async def upload_file(
    file: UploadFile = File(...),
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    ext = os.path.splitext(file.filename.lower())[1]
    audio_video_extensions = {'.mp3', '.mp4', '.mpeg', '.mpga', '.m4a', '.ogg', '.wav', '.webm', '.flac'}
    is_audio_video = (
        file.content_type.startswith("audio/") 
        or file.content_type in ["video/mp4", "video/webm"] 
        or ext in audio_video_extensions
    )

    if file.content_type not in ALLOWED_TYPES and not is_audio_video:
        raise HTTPException(
            status_code=400, 
            detail="Only PDF, TXT, and supported Audio/Video files are allowed."
        )
    
    content = await file.read()

    print(f"Content type received: '{file.content_type}' for file '{file.filename}'")

    size_mb = len(content) / (1024 * 1024)
    if size_mb > MAX_SIZE_MB:
        raise HTTPException(status_code=400, detail=f"File too large. Max size is {MAX_SIZE_MB}MB")
    
    if ext in ['.mp4', '.webm'] or file.content_type in ["video/mp4", "video/webm"]:
        doc_type = "video"
    elif is_audio_video:
        doc_type = "audio"
    else:
        doc_type = "doc"

    content_type = file.content_type
    if is_audio_video and not (content_type.startswith("audio/") or content_type.startswith("video/")):
        content_type = "audio/wav"

    # Text Extraction
    try:
        extraction = extract(content, content_type)
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
        total_pages=extraction.total_pages,
        doc_type=doc_type
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