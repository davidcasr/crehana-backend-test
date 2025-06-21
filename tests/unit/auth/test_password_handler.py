"""Tests unitarios para Password Handler."""
import pytest
from app.auth.password_handler import hash_password, verify_password


@pytest.mark.unit
class TestPasswordHandler:
    """Tests para Password Handler."""
    
    def test_hash_password_success(self):
        """Test hashear contraseña exitosamente."""
        # Arrange
        password = "my_secure_password"
        
        # Act
        hashed = hash_password(password)
        
        # Assert
        assert isinstance(hashed, str)
        assert hashed != password  # Hash debe ser diferente al password original
        assert hashed.startswith("$2b$")  # bcrypt prefix
        assert len(hashed) > 50  # bcrypt hash length
    
    def test_hash_password_different_hashes(self):
        """Test que contraseñas iguales generen hashes diferentes (por salt)."""
        # Arrange
        password = "same_password"
        
        # Act
        hash1 = hash_password(password)
        hash2 = hash_password(password)
        
        # Assert
        assert hash1 != hash2  # Diferentes por el salt random
        assert verify_password(password, hash1)  # Ambos deben verificar correctamente
        assert verify_password(password, hash2)
    
    def test_verify_password_correct(self):
        """Test verificar contraseña correcta."""
        # Arrange
        password = "correct_password"
        hashed = hash_password(password)
        
        # Act
        result = verify_password(password, hashed)
        
        # Assert
        assert result is True
    
    def test_verify_password_incorrect(self):
        """Test verificar contraseña incorrecta."""
        # Arrange
        correct_password = "correct_password"
        wrong_password = "wrong_password"
        hashed = hash_password(correct_password)
        
        # Act
        result = verify_password(wrong_password, hashed)
        
        # Assert
        assert result is False
    
    def test_verify_password_empty_password(self):
        """Test verificar contraseña vacía."""
        # Arrange
        hashed = hash_password("some_password")
        
        # Act
        result = verify_password("", hashed)
        
        # Assert
        assert result is False
    
    def test_verify_password_empty_hash(self):
        """Test verificar con hash vacío."""
        # Arrange
        password = "some_password"
        
        # Act & Assert
        # passlib puede lanzar excepción con hash vacío, lo cual es comportamiento esperado
        try:
            result = verify_password(password, "")
            assert result is False
        except (ValueError, TypeError):
            # Es aceptable que lance excepción con hash inválido
            pass
    
    def test_verify_password_invalid_hash(self):
        """Test verificar con hash inválido."""
        # Arrange
        password = "some_password"
        invalid_hash = "not_a_valid_bcrypt_hash"
        
        # Act & Assert
        # passlib puede lanzar excepción con hash inválido, lo cual es comportamiento esperado
        try:
            result = verify_password(password, invalid_hash)
            assert result is False
        except (ValueError, TypeError):
            # Es aceptable que lance excepción con hash inválido
            pass 