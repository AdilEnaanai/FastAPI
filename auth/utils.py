from passlib.context import CryptContext

# ============================================================================
# CONFIGURATION DU HASHAGE
# ============================================================================

# Context pour hasher les mots de passe avec bcrypt
# bcrypt est l'algorithme recommandé pour les mots de passe
pwd_context = CryptContext(
    schemes=["argon2"],
    deprecated="auto"
)

# ============================================================================
# FONCTIONS UTILITAIRES
# ============================================================================

def hash_password(password: str) -> str:
    """
    Hash un mot de passe en clair.
    
    Le hash est unique même pour des mots de passe identiques
    grâce au "salt" automatique de bcrypt.
    
    Args:
        password: Mot de passe en clair
    
    Returns:
        str: Hash du mot de passe (60 caractères pour bcrypt)
    
    Example:
        >>> hash_password("secret123")
        '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36...'
    """
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Vérifie qu'un mot de passe en clair correspond au hash.
    
    Args:
        plain_password: Mot de passe en clair saisi par l'utilisateur
        hashed_password: Hash stocké en base de données
    
    Returns:
        bool: True si le mot de passe est correct, False sinon
    
    Example:
        >>> hashed = hash_password("secret123")
        >>> verify_password("secret123", hashed)
        True
        >>> verify_password("wrongpassword", hashed)
        False
    """
    return pwd_context.verify(plain_password, hashed_password)
