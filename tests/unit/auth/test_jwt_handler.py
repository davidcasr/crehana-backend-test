"""Tests unitarios para JWT Handler."""
import pytest
from unittest.mock import patch
from datetime import datetime, timedelta
from jose import jwt, JWTError
from fastapi import HTTPException
from app.auth.jwt_handler import create_access_token, decode_access_token, get_user_id_from_token


@pytest.mark.unit
class TestJWTHandler:
    """Tests para JWT Handler."""
    
    @patch('app.auth.jwt_handler.SECRET_KEY', 'test-secret-key-for-testing')
    def test_create_access_token_success(self):
        """Test crear token de acceso exitosamente."""
        # Arrange
        data = {"sub": "123"}
        
        # Act
        token = create_access_token(data)
        
        # Assert
        assert isinstance(token, str)
        assert len(token) > 0
        
        # Verify token can be decoded
        decoded = jwt.decode(token, "test-secret-key-for-testing", algorithms=["HS256"])
        assert decoded["sub"] == "123"
        assert "exp" in decoded
    
    @patch('app.auth.jwt_handler.SECRET_KEY', 'test-secret-key-for-testing')
    @patch('app.auth.jwt_handler.ACCESS_TOKEN_EXPIRE_MINUTES', 30)
    def test_create_access_token_with_custom_expiry(self):
        """Test crear token con tiempo de expiración personalizado."""
        # Arrange
        data = {"sub": "123"}
        expires_delta = timedelta(minutes=60)
        
        # Act
        token = create_access_token(data, expires_delta)
        
        # Assert
        assert isinstance(token, str)
        
        # Verify expiration time
        decoded = jwt.decode(token, "test-secret-key-for-testing", algorithms=["HS256"])
        exp_timestamp = decoded["exp"]
        exp_datetime = datetime.fromtimestamp(exp_timestamp)
        
        # Should expire in approximately 60 minutes (with some tolerance)
        expected_exp = datetime.utcnow() + timedelta(minutes=60)
        time_diff = abs((exp_datetime - expected_exp).total_seconds())
        assert time_diff < 60  # Within 1 minute tolerance
    
    def test_decode_access_token_success(self):
        """Test decodificar token exitosamente."""
        # Arrange
        secret = "test-secret-key"
        payload = {"sub": "123", "exp": datetime.utcnow() + timedelta(minutes=30)}
        token = jwt.encode(payload, secret, algorithm="HS256")
        
        # Act
        with patch('app.auth.jwt_handler.SECRET_KEY', secret):
            result = decode_access_token(token)
        
        # Assert
        assert result["sub"] == "123"
    
    def test_decode_access_token_invalid(self):
        """Test decodificar token inválido."""
        # Arrange
        invalid_token = "invalid.token.here"
        
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            decode_access_token(invalid_token)
        assert exc_info.value.status_code == 401
        assert "Token inválido" in str(exc_info.value.detail)
    
    def test_decode_access_token_expired(self):
        """Test decodificar token expirado."""
        # Arrange
        secret = "test-secret-key"
        payload = {"sub": "123", "exp": datetime.utcnow() - timedelta(minutes=30)}  # Expired
        token = jwt.encode(payload, secret, algorithm="HS256")
        
        # Act & Assert
        with patch('app.auth.jwt_handler.SECRET_KEY', secret):
            with pytest.raises(HTTPException) as exc_info:
                decode_access_token(token)
            assert exc_info.value.status_code == 401
            assert "Token inválido" in str(exc_info.value.detail)
    
    def test_decode_access_token_malformed(self):
        """Test decodificar token malformado."""
        # Arrange
        malformed_token = "malformed"
        
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            decode_access_token(malformed_token)
        assert exc_info.value.status_code == 401
        assert "Token inválido" in str(exc_info.value.detail)
    
    def test_decode_access_token_wrong_signature(self):
        """Test decodificar token con firma incorrecta."""
        # Arrange
        wrong_secret = "wrong-secret"
        correct_secret = "correct-secret"
        payload = {"sub": "123", "exp": datetime.utcnow() + timedelta(minutes=30)}
        token = jwt.encode(payload, wrong_secret, algorithm="HS256")
        
        # Act & Assert
        with patch('app.auth.jwt_handler.SECRET_KEY', correct_secret):
            with pytest.raises(HTTPException) as exc_info:
                decode_access_token(token)
            assert exc_info.value.status_code == 401
            assert "Token inválido" in str(exc_info.value.detail)
    
    def test_get_user_id_from_token_success(self):
        """Test obtener user ID del token exitosamente."""
        # Arrange
        secret = "test-secret-key"
        payload = {"sub": "123", "exp": datetime.utcnow() + timedelta(minutes=30)}
        token = jwt.encode(payload, secret, algorithm="HS256")
        
        # Act
        with patch('app.auth.jwt_handler.SECRET_KEY', secret):
            result = get_user_id_from_token(token)
        
        # Assert
        assert result == 123
    
    def test_get_user_id_from_token_no_sub(self):
        """Test obtener user ID del token sin 'sub'."""
        # Arrange
        secret = "test-secret-key"
        payload = {"exp": datetime.utcnow() + timedelta(minutes=30)}  # No 'sub'
        token = jwt.encode(payload, secret, algorithm="HS256")
        
        # Act & Assert
        with patch('app.auth.jwt_handler.SECRET_KEY', secret):
            with pytest.raises(HTTPException) as exc_info:
                get_user_id_from_token(token)
            assert exc_info.value.status_code == 401
            assert "falta user_id" in str(exc_info.value.detail)
    
    def test_get_user_id_from_token_invalid_user_id(self):
        """Test obtener user ID del token con ID inválido."""
        # Arrange
        secret = "test-secret-key"
        payload = {"sub": "invalid", "exp": datetime.utcnow() + timedelta(minutes=30)}
        token = jwt.encode(payload, secret, algorithm="HS256")
        
        # Act & Assert
        with patch('app.auth.jwt_handler.SECRET_KEY', secret):
            with pytest.raises(HTTPException) as exc_info:
                get_user_id_from_token(token)
            assert exc_info.value.status_code == 401
            assert "user_id no válido" in str(exc_info.value.detail)
    
    def test_get_user_id_from_token_invalid_token(self):
        """Test obtener user ID de token inválido."""
        # Arrange
        invalid_token = "invalid.token"
        
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            get_user_id_from_token(invalid_token)
        assert exc_info.value.status_code == 401
        assert "Token inválido" in str(exc_info.value.detail) 