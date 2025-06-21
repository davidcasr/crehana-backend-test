"""Authentication dependencies for FastAPI."""

from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from .jwt_handler import get_user_id_from_token
from ..application.use_cases.user import UserUseCases
from ..dependencies import get_user_use_cases

# Configurar el esquema de autenticación Bearer
security = HTTPBearer()


async def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> int:
    """
    Obtener el ID del usuario actual desde el token JWT.

    Args:
        credentials: Credenciales HTTP Bearer

    Returns:
        ID del usuario autenticado

    Raises:
        HTTPException: Si el token es inválido
    """
    return get_user_id_from_token(credentials.credentials)


async def get_current_user(
    user_id: int = Depends(get_current_user_id),
    user_use_cases: UserUseCases = Depends(get_user_use_cases),
):
    """
    Obtener el usuario actual completo desde el token JWT.

    Args:
        user_id: ID del usuario desde el token
        user_use_cases: Casos de uso de usuario

    Returns:
        Entidad User del usuario autenticado

    Raises:
        HTTPException: Si el usuario no existe
    """
    try:
        return user_use_cases.get_user_by_id(user_id)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no encontrado",
            headers={"WWW-Authenticate": "Bearer"},
        )


# Dependencia opcional para rutas que pueden funcionar con o sin autenticación
async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(
        HTTPBearer(auto_error=False)
    ),
    user_use_cases: UserUseCases = Depends(get_user_use_cases),
):
    """
    Obtener el usuario actual si está autenticado, None en caso contrario.

    Args:
        credentials: Credenciales HTTP Bearer (opcional)
        user_use_cases: Casos de uso de usuario

    Returns:
        Entidad User si está autenticado, None en caso contrario
    """
    if not credentials:
        return None

    try:
        user_id = get_user_id_from_token(credentials.credentials)
        return user_use_cases.get_user_by_id(user_id)
    except:
        return None
