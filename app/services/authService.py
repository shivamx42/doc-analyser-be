import re

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from httpx import ConnectError

from app.db.supabaseClient import supabase , supabase_admin
from app.pydanticModels import AuthenticatedUser, LoginRequest, LoginResponse, RegisterRequest, RegisterResponse

EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
PASSWORD_MIN_LENGTH = 8

bearer_scheme = HTTPBearer(auto_error=False)


def _validate_register_payload(payload: RegisterRequest) -> tuple[str, str, str]:
    email = payload.email.strip().lower()
    password = payload.password.strip()
    display_name = payload.display_name.strip()

    if not EMAIL_PATTERN.match(email):
        raise HTTPException(400, "Enter a valid email address")

    if len(password) < PASSWORD_MIN_LENGTH:
        raise HTTPException(
            400,
            f"Password must be at least {PASSWORD_MIN_LENGTH} characters long",
        )

    return email, password, display_name


def _validate_login_payload(payload: LoginRequest) -> tuple[str, str]:
    email = payload.email.strip().lower()
    password = payload.password.strip()

    if not EMAIL_PATTERN.match(email):
        raise HTTPException(400, "Enter a valid email address")

    if not password:
        raise HTTPException(400, "Password is required")

    return email, password


# supabse account creation error handling
def _handle_auth_creation_error(error: Exception) -> None:
    status = getattr(error, "status", None)
    code = getattr(error, "code", None)

    print(status, code)

    # duplicate check
    if status == 422:
        if code == "email_exists":
            raise HTTPException(409, "An account with this email already exists")
        raise HTTPException(400, "Invalid user data")

    if status == 401:
        raise HTTPException(401, "Unauthorized request to auth service")

    if status == 403:
        raise HTTPException(403, "Insufficient permissions")

    if status == 429:
        raise HTTPException(429, "Too many requests")

    if status and status >= 500:
        raise HTTPException(502, "Auth service error")

    raise HTTPException(502, "Unhandled auth error")


# supabase login error handling
def _handle_login_error(error: Exception) -> None:
    status = getattr(error, "status", None)
    code = getattr(error, "code", None)

    print(status, code)

    if status == 400:
        raise HTTPException(400, "Invalid login request")

    if status == 403:
        raise HTTPException(403, "Login not allowed")

    if status == 429:
        raise HTTPException(429, "Too many login attempts")

    if status and status >= 500:
        raise HTTPException(502, "Auth service error")

    raise HTTPException(502, "Unhandled login error")

# supabase auth validation error handling
def _handle_auth_validation_error(error: Exception) -> None:
    status = getattr(error, "status", None)
    code = getattr(error, "code", None)
    print(status, code)

    if status == 401:
        raise HTTPException(401, "Invalid or expired access token")

    if status == 403:
        raise HTTPException(403, "Access forbidden")

    if status == 429:
        raise HTTPException(429, "Too many auth requests")

    if status and status >= 500:
        raise HTTPException(502, "Auth validation failed")

    raise HTTPException(502, "Unhandled auth validation error")

def register_user(payload: RegisterRequest) -> RegisterResponse:
    email, password, display_name = _validate_register_payload(payload)

    try:
        auth_response = supabase_admin.auth.admin.create_user({
            "email": email,
            "password": password,
            "email_confirm": True,
            "user_metadata": {"display_name": display_name},
        })
    except ConnectError as error:
        raise HTTPException(502, "Could not reach Supabase auth service") from error
    except Exception as error:
        _handle_auth_creation_error(error)

    user = getattr(auth_response, "user", None)
    if user is None:
        raise HTTPException(502, "Supabase did not return the created user")

    try:
        supabase.table("profiles").insert({
            "id": user.id,
            "display_name": display_name,
        }).execute()
    except Exception as error:
        try:
            supabase.auth.admin.delete_user(user.id)
        except Exception:
            pass
        raise HTTPException(
            502,
            "Account was created, but profile setup failed",
        ) from error

    return RegisterResponse(
        user_id=user.id,
        email=user.email,
        display_name=display_name,
        message="Account created successfully",
    )


def login_user(payload: LoginRequest) -> LoginResponse:

    email, password = _validate_login_payload(payload)

    try:
        auth_response = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password,
        })
    except ConnectError as error:
        raise HTTPException(502, "Could not reach auth service") from error
    except Exception as error:
        _handle_login_error(error)

    session = getattr(auth_response, "session", None)
    user = getattr(auth_response, "user", None)

    if session is None or user is None:
        raise HTTPException(401, "Invalid login credentials")

    return {
        "access_token": session.access_token,
        "refresh_token": session.refresh_token,
        "user_id": str(user.id),
        "email": user.email,
        "display_name": user.user_metadata.get("display_name")
    }

def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme)) -> AuthenticatedUser:
    if credentials is None or not credentials.credentials.strip():
        raise HTTPException(401, "Authentication required")

    try:
        auth_response = supabase.auth.get_user(credentials.credentials)
    except ConnectError as error:
        raise HTTPException(502, "Could not validate token") from error
    except Exception as error:
        _handle_auth_validation_error(error)

    user = getattr(auth_response, "user", None)
    if user is None:
        raise HTTPException(401, "Invalid or expired access token")

    return AuthenticatedUser(
        id=user.id,
        email=getattr(user, "email", None),
    )