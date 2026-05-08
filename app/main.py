import os

from fastapi import FastAPI
from app.routers import upload, query, auth, deleteDocument
from fastapi.middleware.cors import CORSMiddleware
from app.routers import getDocuments

app = FastAPI()

CORS_ALLOWED_ORIGINS = os.getenv("CORS_ALLOWED_ORIGINS", "").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload.router, prefix="/api")
app.include_router(query.router, prefix="/api")
app.include_router(auth.router, prefix="/api")
app.include_router(getDocuments.router, prefix="/api")
app.include_router(deleteDocument.router, prefix="/api")

@app.get("/")
def home():
    return {"message": "server running"}