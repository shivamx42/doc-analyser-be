create or replace function match_chunks(
    query_embedding vector(384),
    match_count int,
    filter_document_id uuid default null
)
returns table(
    id uuid,
    document_id uuid,
    content text,
    similarity float
)
language plpgsql
as $$
begin
    return query
    select
        c.id,
        c.document_id,
        c.content,
        1 - (c.embedding <=> query_embedding) as similarity
    from chunks c
    where
        filter_document_id is null or c.document_id = filter_document_id
    order by c.embedding <=> query_embedding
    limit match_count;
end;
$$;