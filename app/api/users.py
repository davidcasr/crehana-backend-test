"""User management API endpoints."""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from ..application.dtos import (
    UserUpdateRequest,
    UserResponse,
)
from ..application.use_cases.user import UserUseCases
from ..dependencies import get_user_use_cases
from ..domain.exceptions import (
    EntityNotFoundException,
    InvalidDataException,
    DuplicateEntityException,
)
from ..domain.models.enums import UserStatus

router = APIRouter(prefix="/api/v1/users", tags=["Users"])



@router.get("/", response_model=List[UserResponse])
def list_users(
    user_status: Optional[UserStatus] = Query(None, alias="status", description="Filter by user status"),
    user_use_cases: UserUseCases = Depends(get_user_use_cases),
):
    """
    Get all users with optional status filter.
    
    - **status**: Filter by user status (active, inactive, suspended)
    """
    try:
        users = user_use_cases.get_all_users(status=user_status)
        return [UserResponse.from_entity(user) for user in users]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve users",
        )


@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: int,
    user_use_cases: UserUseCases = Depends(get_user_use_cases),
):
    """
    Get a user by ID.
    """
    try:
        user = user_use_cases.get_user_by_id(user_id)
        return UserResponse.from_entity(user)
    except EntityNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except InvalidDataException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/by-username/{username}", response_model=UserResponse)
def get_user_by_username(
    username: str,
    user_use_cases: UserUseCases = Depends(get_user_use_cases),
):
    """
    Get a user by username.
    """
    try:
        user = user_use_cases.get_user_by_username(username)
        return UserResponse.from_entity(user)
    except EntityNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except InvalidDataException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/by-email/{email}", response_model=UserResponse)
def get_user_by_email(
    email: str,
    user_use_cases: UserUseCases = Depends(get_user_use_cases),
):
    """
    Get a user by email.
    """
    try:
        user = user_use_cases.get_user_by_email(email)
        return UserResponse.from_entity(user)
    except EntityNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except InvalidDataException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    user_data: UserUpdateRequest,
    user_use_cases: UserUseCases = Depends(get_user_use_cases),
):
    """
    Update a user.
    
    - **username**: New username (optional, 3-50 characters, unique)
    - **email**: New email (optional, unique)
    - **full_name**: New full name (optional)
    - **status**: New status (optional)
    """
    try:
        user = user_use_cases.update_user(
            user_id=user_id,
            username=user_data.username,
            email=user_data.email,
            full_name=user_data.full_name,
            status=user_data.status,
        )
        return UserResponse.from_entity(user)
    except EntityNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except InvalidDataException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except DuplicateEntityException as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        )


@router.patch("/{user_id}/deactivate", response_model=UserResponse)
def deactivate_user(
    user_id: int,
    user_use_cases: UserUseCases = Depends(get_user_use_cases),
):
    """
    Deactivate a user (set status to inactive).
    """
    try:
        user = user_use_cases.deactivate_user(user_id)
        return UserResponse.from_entity(user)
    except EntityNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.patch("/{user_id}/activate", response_model=UserResponse)
def activate_user(
    user_id: int,
    user_use_cases: UserUseCases = Depends(get_user_use_cases),
):
    """
    Activate a user (set status to active).
    """
    try:
        user = user_use_cases.activate_user(user_id)
        return UserResponse.from_entity(user)
    except EntityNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int,
    user_use_cases: UserUseCases = Depends(get_user_use_cases),
):
    """
    Delete a user.
    
    **Warning**: This will permanently delete the user and may affect associated tasks.
    """
    try:
        success = user_use_cases.delete_user(user_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with id {user_id} not found",
            )
    except EntityNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) 