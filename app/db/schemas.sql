create table documents (
    id uuid primary key default gen_random_uuid(),
    owner_id uuid not null references auth.users(id) on delete cascade,
    filename text not null,
    content_type text not null,
    total_pages int not null,
    created_at timestamp default now()
);

create table profiles (
    id uuid primary key references auth.users(id) on delete cascade,
    display_name text,
    created_at timestamp default now(),
    updated_at timestamp default now()
);

create index documents_owner_id_idx on documents(owner_id);

create table chunks (
    id uuid primary key default gen_random_uuid(),
    document_id uuid references documents(id) on delete cascade,
    content text not null,
    embedding vector(384),
    chunk_index int,
    created_at timestamp default now()
);