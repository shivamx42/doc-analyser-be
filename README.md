# Backend Overview

This backend powers the files analysis workflow for **FILE INSIGHT**.
It exposes a FastAPI API that lets authenticated users upload documents, store vector embeddings, search the most relevant chunks, and generate grounded answers from the uploaded content.
...
### Live Deployment
- **Swagger UI**: [https://file-insight.duckdns.org/docs](https://file-insight.duckdns.org/docs)
- **Frontend**: [https://file-insight.netlify.app](https://file-insight.netlify.app)


## What This Backend Does

- Accepts `PDF`, `TXT`, and supported `Audio` & `Video` uploads.
- Extracts document text.
- Falls back to OCR for image-only PDFs.
- Transcribes speech from audio/video files using the Groq Speech-to-Text API.
- Splits text (extracted or transcribed) into smaller chunks for semantic search.
- Generates embeddings with `sentence-transformers`.
- Stores document metadata, chunks, and embeddings in Supabase (tagging files with type `doc`, `audio`, or `video`).
- Retrieves the most relevant chunks for a user question using PostgreSQL vector similarity.
- Sends the retrieved context to Groq to generate a final answer.
- **Generates shareable public links** for specific document subsets, allowing unauthenticated querying.


## Main Request Flow

### 1. Upload

`POST /api/upload`

The upload route:

- validates the file type and size (supports PDF, TXT, and audio/video up to 10MB)
- extracts text from the file (handles PDF text, OCR fallback, or Groq Speech-to-Text transcription for audio/video)
- chunks the extracted/transcribed text
- generates embeddings for each chunk
- stores the document record in `documents` (saving document type as `doc`, `audio`, or `video`)
- stores chunk content and embeddings in `chunks`

Relevant files:

- `app/routers/upload.py`
- `app/services/extractor.py`
- `app/services/transcriber.py`
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

### 5. Document Sharing (Public)

Users can generate a unique token for a selection of documents. Anyone with the token can query those documents without an account.

- `GET /api/share/{token}`: Get share metadata (owner name, document names).
- `POST /api/share/{token}/query`: Query the shared documents.

Relevant files:

- `app/routers/share.py`
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
      share.py               # generate and handle public share links
    services/
      authService.py         # auth validation and Supabase auth logic
      extractor.py           # PDF/TXT extraction and OCR fallback
      transcriber.py         # Groq audio/video transcription
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
- `documents`: stores uploaded document metadata, including a `type` column (`doc`, `audio`, or `video`)
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
- `GROQ_SPEECH_MODEL`     # e.g., whisper-large-v3-turbo for transcribing audio/video uploads


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
- Audio and video files are transcribed to text using the Groq Whisper Speech-to-Text API before chunking and embedding.
- Supported audio/video formats/extensions: `.mp3`, `.mp4`, `.mpeg`, `.mpga`, `.m4a`, `.ogg`, `.wav`, `.webm`, `.flac`.
- File size limit is 10MB for all documents and media.
- Embeddings are generated with `all-MiniLM-L6-v2`, which matches the `vector(384)` schema.
- Authorization is enforced per user before document search or deletion.
- The answer generator is instructed to stay grounded in the retrieved document content.