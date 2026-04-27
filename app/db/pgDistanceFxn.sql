create or replace function match_chunks(
    query_embedding vector(384),
    match_count int,
    filter_document_ids uuid[] default null,
    filter_owner_id uuid default null,
    min_similarity float default 0.3
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
    join documents d on d.id = c.document_id
    where
        (
            filter_document_ids is null
            or array_length(filter_document_ids, 1) is null
            or c.document_id = any(filter_document_ids)
        )
        and (filter_owner_id is null or d.owner_id = filter_owner_id)
        and 1 - (c.embedding <=> query_embedding) >= min_similarity
    order by c.embedding <=> query_embedding
    limit match_count;
end;
$$;