import os
import secrets
from fastapi import APIRouter, HTTPException, Depends, Request
from app.pydanticModels import ShareRequest, ShareResponse, SharedLinkInfo, SharedQueryRequest, QueryResponse, ChunkResult, AuthenticatedUser

from app.services.supabaseStore import create_shared_link, get_shared_link_by_token, get_documents_by_ids, search_chunks

from app.services.authService import get_current_user
from app.services.embedder import generate_embeddings
from app.services.generateAnswer import generate_answer

router = APIRouter()

@router.post("/share", response_model=ShareResponse)
async def share_documents(request: ShareRequest, current_user: AuthenticatedUser = Depends(get_current_user), req: Request = None):
    if not request.document_ids:
        raise HTTPException(status_code=400, detail="No documents selected")
    
    token = secrets.token_urlsafe(16)
    document_ids = [str(did) for did in request.document_ids]
    
    try:
        # Only inserting document ids and not names, so that later if the document is deleted, we can handle it
        owner_name = current_user.display_name or "Unknown User"
        create_shared_link(str(current_user.id), owner_name, document_ids, token)
        
        # Generate frontend URL
        frontend_url = os.getenv("CORS_ALLOWED_ORIGINS")
        share_url = f"{frontend_url}/share/{token}"
        
        return ShareResponse(token=token, share_url=share_url)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating shared link: {str(e)}")

@router.get("/share/{token}", response_model=SharedLinkInfo)
async def get_share_info(token: str):
    shared_link = get_shared_link_by_token(token)
    if not shared_link:
        raise HTTPException(status_code=404, detail="Shared link not found")
    
    # Filter documents to only include those that still exist
    documents = get_documents_by_ids(shared_link["document_ids"])
    if not documents:
        raise HTTPException(status_code=410, detail="The documents in this shared link are no longer available")

    document_names = [doc["filename"] for doc in documents]
    
    return SharedLinkInfo(
        document_names=document_names,
        owner_name=shared_link.get("owner_name", "Unknown User")
    )

@router.post("/share/{token}/query", response_model=QueryResponse)
async def shared_query(token: str, request: SharedQueryRequest):
    shared_link = get_shared_link_by_token(token)

    if not shared_link:
        raise HTTPException(status_code=404, detail="Shared link not found")
    
    # Get only the IDs that still exist
    documents = get_documents_by_ids(shared_link["document_ids"])
    valid_document_ids = [str(doc["id"]) for doc in documents]

    if not valid_document_ids:
        raise HTTPException(status_code=410, detail="The documents in this shared link are no longer available")

    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")

    question_embedding = generate_embeddings([request.question])[0]

    raw_results = search_chunks(
        query_embedding=question_embedding,
        owner_id=None,
        document_ids=valid_document_ids
    )

    if not raw_results:
        return QueryResponse(
            question=request.question,
            answer="Could not find relevant content in the shared documents.",
            results=[]
        )
    
    try:
        answer = generate_answer(request.question, raw_results)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating answer: {str(e)}")

    results = [ChunkResult(**r) for r in raw_results]

    return QueryResponse(
        question=request.question,
        answer=answer,
        results=results
    )