"""JWT token handling utilities."""

import os
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from fastapi import HTTPException, status

# Configuración JWT (usar variables de entorno en producción)
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Crear un token JWT de acceso.
    
    Args:
        data: Datos a incluir en el token
        expires_delta: Tiempo de expiración personalizado
    
    Returns:
        Token JWT como string
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> Dict[str, Any]:
    """
    Decodificar y validar un token JWT.
    
    Args:
        token: Token JWT a decodificar
    
    Returns:
        Payload del token decodificado
    
    Raises:
        HTTPException: Si el token es inválido o ha expirado
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido",
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_user_id_from_token(token: str) -> int:
    """
    Extraer el ID del usuario desde un token JWT.
    
    Args:
        token: Token JWT
    
    Returns:
        ID del usuario
    
    Raises:
        HTTPException: Si el token no contiene user_id válido
    """
    payload = decode_access_token(token)
    user_id_str: str = payload.get("sub")
    
    if user_id_str is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido: falta user_id",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        return int(user_id_str)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido: user_id no válido",
            headers={"WWW-Authenticate": "Bearer"},
        ) 