from pydantic import BaseModel, EmailStr, Field
from models.user import Role

# ============================================================================
# SCHÉMAS USER
# ============================================================================

class UserBase(BaseModel):
    """Schéma de base pour un utilisateur"""
    username: str = Field(..., min_length=3, max_length=64)
    email: EmailStr

class UserCreate(UserBase):
    """
    Schéma pour créer un utilisateur.
    Inclut le mot de passe en clair (sera hashé côté serveur).
    """
    password: str = Field(..., min_length=6, max_length=64)
    role: Role = Role.USER  # Par défaut USER, mais modifiable

class UserResponse(UserBase):
    """
    Schéma pour retourner un utilisateur.
    Ne contient JAMAIS le mot de passe (même hashé).
    """
    id: int
    role: Role
    is_active: bool
    
    class Config:
        from_attributes = True

# ============================================================================
# SCHÉMAS AUTHENTIFICATION
# ============================================================================

class Token(BaseModel):
    """
    Schéma pour retourner un token JWT après login.
    
    Example:
        {
            "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
            "token_type": "bearer"
        }
    """
    access_token: str
    token_type: str

class TokenData(BaseModel):
    """
    Données contenues dans le token JWT (payload).
    Utilisé pour décoder le token et identifier l'utilisateur.
    """
    username: str | None = None
    role: str | None = None

class LoginRequest(BaseModel):
    """
    Schéma pour la requête de login.
    
    Example:
        {
            "username": "john",
            "password": "secret123"
        }
    """
    username: str
    password: str
