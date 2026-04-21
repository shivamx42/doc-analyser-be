from fastapi import APIRouter, Depends

from app.pydanticModels import AuthenticatedUser, DocumentListItem, DocumentListResponse
from app.services.authService import get_current_user
from app.services.supabaseStore import list_user_documents

router = APIRouter()

@router.get("/documents", response_model=DocumentListResponse)
async def list_documents(current_user: AuthenticatedUser = Depends(get_current_user)):
    raw_documents = list_user_documents(str(current_user.id))
    return DocumentListResponse(
        documents=[DocumentListItem(**document) for document in raw_documents]
    )