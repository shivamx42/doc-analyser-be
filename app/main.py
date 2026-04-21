from fastapi import FastAPI
from app.routers import upload, query, auth
from fastapi.middleware.cors import CORSMiddleware
from app.routers import getDocuments

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload.router, prefix="/api")
app.include_router(query.router, prefix="/api")
app.include_router(auth.router, prefix="/api")
app.include_router(getDocuments.router, prefix="/api")

@app.get("/")
def home():
    return {"message": "server running"}