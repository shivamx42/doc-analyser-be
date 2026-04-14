create table documents (
    id uuid primary key default gen_random_uuid(),
    filename text not null,
    content_type text not null,
    total_pages int not null,
    created_at timestamp default now()
);

create table chunks (
    id uuid primary key default gen_random_uuid(),
    document_id uuid references documents(id) on delete cascade,
    content text not null,
    embedding vector(384),
    page_number int,
    chunk_index int,
    created_at timestamp default now()
);