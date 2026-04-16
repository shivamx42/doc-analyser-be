from fastapi import APIRouter, HTTPException
from app.schemas import QueryRequest, QueryResponse, ChunkResult
from app.services.embedder import generate_embeddings
from app.services.supabaseStore import search_chunks
from app.services.generateAnswer import generate_answer

router = APIRouter()

@router.post("/query", response_model=QueryResponse)
async def get_results_from_query(request: QueryRequest):
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")

    question_embedding = generate_embeddings([request.question])[0]

    raw_results = search_chunks(
        query_embedding=question_embedding,
        document_id=request.document_id
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