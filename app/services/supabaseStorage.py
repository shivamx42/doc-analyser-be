from app.db.supabaseClient import supabase

def store_document(filename: str, content_type: str, total_pages: int) -> str:
    result = supabase.table("documents").insert({
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