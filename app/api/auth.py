"""Authentication API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from ..application.dtos import (
    LoginRequest,
    LoginResponse,
    RegisterRequest,
    UserResponse,
    ChangePasswordRequest,
)
from ..application.use_cases.user import UserUseCases
from ..auth.jwt_handler import create_access_token
from ..auth.password_handler import hash_password, verify_password
from ..auth.dependencies import get_current_user
from ..dependencies import get_user_use_cases
from ..domain.exceptions import DuplicateEntityException, EntityNotFoundException

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
async def register(
    request: RegisterRequest, user_use_cases: UserUseCases = Depends(get_user_use_cases)
):
    """
    Register a new user.

    Creates a new user account with the provided information.
    The password will be securely hashed before storage.
    """
    try:
        # Hash the password
        password_hash = hash_password(request.password)

        # Create user with hashed password
        user = user_use_cases.create_user(
            username=request.username,
            email=request.email,
            full_name=request.full_name,
            password_hash=password_hash,
        )

        return UserResponse.from_entity(user)

    except DuplicateEntityException as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor",
        )


@router.post("/login", response_model=LoginResponse)
async def login(
    request: LoginRequest, user_use_cases: UserUseCases = Depends(get_user_use_cases)
):
    """
    Login user and return JWT token.

    Authenticates user with username/email and password,
    returns JWT access token on success.
    """
    try:
        # Get user by username or email
        user = user_use_cases.authenticate_user(request.username)

        if not user or not user.password_hash:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuario o contraseña incorrectos",
            )

        # Verify password
        if not verify_password(request.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuario o contraseña incorrectos",
            )

        # Create access token
        access_token = create_access_token(data={"sub": str(user.id)})

        return LoginResponse(
            access_token=access_token,
            token_type="bearer",
            user=UserResponse.from_entity(user),
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor",
        )


@router.post("/login-form", response_model=LoginResponse)
async def login_form(
    form_data: OAuth2PasswordRequestForm = Depends(),
    user_use_cases: UserUseCases = Depends(get_user_use_cases),
):
    """
    Login using OAuth2 password form (for Swagger UI).

    Alternative login endpoint that accepts form data,
    compatible with Swagger UI's "Authorize" button.
    """
    # Create LoginRequest from form data
    login_request = LoginRequest(
        username=form_data.username, password=form_data.password
    )

    # Use the same logic as regular login
    return await login(login_request, user_use_cases)


@router.post("/change-password")
async def change_password(
    request: ChangePasswordRequest,
    current_user=Depends(get_current_user),
    user_use_cases: UserUseCases = Depends(get_user_use_cases),
):
    """
    Change user password.

    Requires authentication. User must provide current password
    and new password to change their password.
    """
    try:
        # Verify current password
        if not current_user.password_hash or not verify_password(
            request.current_password, current_user.password_hash
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Contraseña actual incorrecta",
            )

        # Hash new password
        new_password_hash = hash_password(request.new_password)

        # Update user password
        user_use_cases.update_user_password(current_user.id, new_password_hash)

        return {"message": "Contraseña actualizada exitosamente"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor",
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user=Depends(get_current_user)):
    """
    Get current user information.

    Returns the profile information of the currently authenticated user.
    Requires valid JWT token in Authorization header.
    """
    return UserResponse.from_entity(current_user)
