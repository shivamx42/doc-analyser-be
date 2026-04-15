from fastapi import FastAPI
from app.routers import upload, query

app = FastAPI()

app.include_router(upload.router, prefix="/api")
app.include_router(query.router, prefix="/api")

@app.get("/")
def home():
    return {"message": "server running"}