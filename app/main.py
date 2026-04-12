from fastapi import FastAPI
from app.routers import upload

app = FastAPI()

app.include_router(upload.router, prefix="/api")

@app.get("/")
def home():
    return {"message": "server running"}