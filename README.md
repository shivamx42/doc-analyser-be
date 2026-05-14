# Backend Overview

This backend powers the document analysis workflow for **Doc Analyser**.
It exposes a FastAPI API that lets authenticated users upload documents, store vector embeddings, search the most relevant chunks, and generate grounded answers from the uploaded content.

## What This Backend Does

- Accepts `PDF` and `TXT` uploads.
- Extracts document text.
- Falls back to OCR for image-only PDFs.
- Splits text into smaller chunks for semantic search.
- Generates embeddings with `sentence-transformers`.
- Stores document metadata and chunks in Supabase.
- Retrieves the most relevant chunks for a user question using PostgreSQL vector similarity.
- Sends the retrieved context to Groq to generate a final answer.

## Main Request Flow

### 1. Upload

`POST /api/upload`

The upload route:

- validates the file type and size
- extracts text from the file
- chunks the extracted text
- generates embeddings for each chunk
- stores the document record in `documents`
- stores chunk content and embeddings in `chunks`

Relevant files:

- `app/routers/upload.py`
- `app/services/extractor.py`
- `app/services/chunker.py`
- `app/services/embedder.py`
- `app/services/supabaseStore.py`

### 2. Ask a Question

`POST /api/query`

The query route:

- validates the question
- verifies the requested documents belong to the logged-in user
- creates an embedding for the question
- calls the `match_chunks` Postgres function to find similar chunks
- sends the retrieved content to Groq for answer generation
- returns both the answer and the matched chunks

Relevant files:

- `app/routers/query.py`
- `app/services/embedder.py`
- `app/services/supabaseStore.py`
- `app/services/generateAnswer.py`
- `app/db/pgDistanceFxn.sql`

### 3. Authentication

The backend also handles account registration, login, and bearer-token validation through Supabase Auth.

Relevant files:

- `app/routers/auth.py`
- `app/services/authService.py`

### 4. Document Library

Users can list and delete their uploaded documents.

Relevant files:

- `app/routers/getDocuments.py`
- `app/routers/deleteDocument.py`
- `app/services/supabaseStore.py`

## Project Structure

```text
backend/
  app/
    db/
      pgDistanceFxn.sql      # vector search SQL function
      schemas.sql            # core database tables
      supabaseClient.py      # Supabase client setup
    routers/
      auth.py                # register/login endpoints
      upload.py              # file upload endpoint
      query.py               # question-answering endpoint
      getDocuments.py        # list uploaded documents
      deleteDocument.py      # delete a document
    services/
      authService.py         # auth validation and Supabase auth logic
      extractor.py           # PDF/TXT extraction and OCR fallback
      chunker.py             # chunking logic
      embedder.py            # sentence-transformer embeddings
      supabaseStore.py       # DB reads/writes
      generateAnswer.py      # Groq answer generation
    main.py                  # FastAPI app entry point
    pydanticModels.py        # request/response models
  Dockerfile
  requirements.txt
```

## Database Design

The backend relies on three main tables:

- `profiles`: stores user display names
- `documents`: stores uploaded document metadata
- `chunks`: stores chunk text and `vector(384)` embeddings

`match_chunks(...)` in `app/db/pgDistanceFxn.sql` performs similarity search by:

- filtering results to the current user
- optionally filtering to selected document IDs
- computing similarity with pgvector distance
- returning the top matching chunks above a threshold

## Environment Variables

The backend expects these values:

- `CORS_ALLOWED_ORIGINS`
- `SUPABASE_URL`
- `SUPABASE_KEY`
- `GROQ_API_KEY`
- `GROQ_MODEL`


## Run Locally

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

The API root is available at:

```text
http://127.0.0.1:8000/
```

## Important Notes

- PDF extraction first uses embedded text, then OCR if no text is found.
- Embeddings are generated with `all-MiniLM-L6-v2`, which matches the `vector(384)` schema.
- Authorization is enforced per user before document search or deletion.
- The answer generator is instructed to stay grounded in the retrieved document content.
