from fastapi import APIRouter, status

from app.pydanticModels import LoginRequest, LoginResponse, RegisterRequest, RegisterResponse
from app.services.authService import login_user, register_user

router = APIRouter()

@router.post("/auth/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
async def register_account(request: RegisterRequest):
    return register_user(request)

@router.post("/auth/login", response_model=LoginResponse, status_code=status.HTTP_200_OK)
async def login(request: LoginRequest):
    return login_user(request)