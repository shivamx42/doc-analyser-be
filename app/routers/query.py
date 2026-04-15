from fastapi import APIRouter, HTTPException
from app.schemas import QueryRequest, QueryResponse, ChunkResult
from app.services.embedder import generate_embeddings
from app.services.supabaseStore import search_chunks

router = APIRouter()

@router.post("/query", response_model=QueryResponse)
async def get_results_from_query(request: QueryRequest):
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")

    # Embedding the question
    question_embedding = generate_embeddings([request.question])[0]

    # Search
    raw_results = search_chunks(
        query_embedding=question_embedding,
        document_id=request.document_id
    )

    results = [
        ChunkResult(**r)
        for r in raw_results
    ]

    return QueryResponse(question=request.question, results=results)