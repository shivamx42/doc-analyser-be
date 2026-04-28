from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from app.pydanticModels import AuthenticatedUser, DeleteDocumentResponse
from app.services.authService import get_current_user
from app.services.supabaseStore import delete_user_document

router = APIRouter()


@router.delete("/documents/delete/{document_id}", response_model=DeleteDocumentResponse)
async def delete_document(
    document_id: UUID,
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    deleted = delete_user_document(
        owner_id=str(current_user.id),
        document_id=str(document_id),
    )

    if not deleted:
        raise HTTPException(status_code=404, detail="Document not found")

    return DeleteDocumentResponse(
        document_id=document_id,
        message="Document deleted successfully",
    )