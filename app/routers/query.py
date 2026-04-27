from fastapi import APIRouter, HTTPException, Depends
from app.pydanticModels import QueryRequest, QueryResponse, ChunkResult, AuthenticatedUser
from app.services.embedder import generate_embeddings
from app.services.supabaseStore import list_user_documents, search_chunks
from app.services.generateAnswer import generate_answer
from app.services.authService import get_current_user

router = APIRouter()

@router.post("/query", response_model=QueryResponse)
async def get_results_from_query(
    request: QueryRequest,
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")

    if len(request.document_ids) > 20:
        raise HTTPException(status_code=400, detail="You can search up to 20 documents at a time")

    selected_document_ids = [str(document_id) for document_id in request.document_ids]

    if selected_document_ids:
        owned_documents = list_user_documents(str(current_user.id))
        owned_document_ids = {document["id"] for document in owned_documents}

        if any(document_id not in owned_document_ids for document_id in selected_document_ids):
            raise HTTPException(status_code=404, detail="Document not found")

    question_embedding = generate_embeddings([request.question])[0]

    raw_results = search_chunks(
        query_embedding=question_embedding,
        owner_id=str(current_user.id),
        document_ids=selected_document_ids or None
    )

    if not raw_results:
        return QueryResponse(
            question=request.question,
            answer="Could not find relevant content in the document. Try giving more relevant details",
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