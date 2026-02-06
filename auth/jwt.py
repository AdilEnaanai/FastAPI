from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from schemas.user import TokenData
import os
from dotenv import load_dotenv

load_dotenv()

# ============================================================================
# CONFIGURATION JWT
# ============================================================================

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

# ============================================================================
# FONCTIONS JWT
# ============================================================================

def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """
    Crée un token JWT signé.
    
    Le token contient les données de l'utilisateur (username, role)
    et une date d'expiration.
    
    Args:
        data: Dictionnaire de données à encoder (ex: {"sub": "ali", "role": "user"})
        expires_delta: Durée de validité du token (défaut: 30 min)
    
    Returns:
        str: Token JWT signé
    
    Example:
        >>> token = create_access_token({"sub": "ali", "role": "user"})
        >>> print(token)
        'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...'
    
    Structure du token JWT:
        HEADER.PAYLOAD.SIGNATURE
        
        HEADER: {"alg": "HS256", "typ": "JWT"}
        PAYLOAD: {"sub": "john", "role": "user", "exp": 1234567890}
        SIGNATURE: hash(HEADER + PAYLOAD + SECRET_KEY)
    """
    # Copier les données pour ne pas modifier l'original
    to_encode = data.copy()
    
    # Définir la date d'expiration
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    # Ajouter l'expiration au payload
    to_encode.update({"exp": expire})
    
    # Encoder et signer le token
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    return encoded_jwt

def decode_access_token(token: str) -> TokenData | None:
    """
    Décode et valide un token JWT.
    
    Vérifie la signature et l'expiration du token.
    
    Args:
        token: Token JWT à décoder
    
    Returns:
        TokenData | None: Données du token si valide, None sinon
    
    Example:
        >>> token = create_access_token({"sub": "john", "role": "user"})
        >>> data = decode_access_token(token)
        >>> print(data.username)
        'john'
    """
    try:
        # Décoder le token avec vérification de signature
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # Extraire le username (claim "sub" = subject)
        username: str = payload.get("sub")
        role: str = payload.get("role")
        
        if username is None:
            return None
        
        # Retourner les données validées
        return TokenData(username=username, role=role)
        
    except JWTError:
        # Token invalide, expiré ou signature incorrecte
        return None
