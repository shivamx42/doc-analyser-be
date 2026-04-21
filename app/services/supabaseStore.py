from typing import Optional

from app.db.supabaseClient import supabase

def store_document(owner_id: str, filename: str, content_type: str, total_pages: int) -> str:
    result = supabase.table("documents").insert({
        "owner_id": owner_id,
        "filename": filename,
        "content_type": content_type,
        "total_pages": total_pages
    }).execute()

    return result.data[0]["id"]

def store_chunks(document_id: str, chunks: list[str], embeddings: list[list[float]]):
    rows=[]

    for chunk, embedding in zip(chunks, embeddings):
        rows.append({
            "document_id": document_id,
            "content": chunk,
            "embedding": embedding 
        })
    
    supabase.table("chunks").insert(rows).execute()

def list_user_documents(owner_id: str) -> list[dict]:
    result = (
        supabase.table("documents")
        .select("id, filename, content_type, total_pages, created_at")
        .eq("owner_id", owner_id)
        .order("created_at", desc=True)
        .execute()
    )

    return result.data or []

def search_chunks(owner_id: str, query_embedding: list[float], document_id: Optional[str] = None, match_count: int = 3, min_similarity: float = 0.3) -> list[dict]:
    result = supabase.rpc("match_chunks", {
        "query_embedding": query_embedding,
        "match_count": match_count,
        "filter_owner_id": owner_id,
        "filter_document_id": document_id,
        "min_similarity": min_similarity
    }).execute()

    return result.data or []