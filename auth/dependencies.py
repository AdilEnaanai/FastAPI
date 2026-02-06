from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from database import get_db
from models.user import User, Role
from auth.jwt import decode_access_token

# ============================================================================
# CONFIGURATION SECURITY
# ============================================================================

# Schéma de sécurité Bearer Token
# L'utilisateur doit envoyer le header: Authorization: Bearer <token>
security = HTTPBearer()

# ============================================================================
# DEPENDENCY: RÉCUPÉRER L'UTILISATEUR CONNECTÉ
# ============================================================================

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Dependency qui récupère l'utilisateur actuellement connecté.
    
    Utilisée pour protéger les routes nécessitant une authentification.
    
    Processus:
        1. Récupère le token depuis le header Authorization
        2. Décode et valide le token JWT
        3. Cherche l'utilisateur en BDD
        4. Vérifie que le compte est actif
        5. Retourne l'utilisateur
    
    Args:
        credentials: Token Bearer extrait du header (automatique)
        db: Session BDD
    
    Returns:
        User: L'utilisateur connecté
    
    Raises:
        HTTPException 401: Si le token est invalide ou l'utilisateur n'existe pas
    
    Usage dans un endpoint:
        @app.get("/protected")
        def protected_route(current_user: User = Depends(get_current_user)):
            return {"message": f"Hello {current_user.username}"}
    """
    # Extraire le token du header Authorization
    token = credentials.credentials
    
    # Exception à lever si l'authentification échoue
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Impossible de valider les identifiants",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # Décoder le token
    token_data = decode_access_token(token)
    
    if token_data is None or token_data.username is None:
        raise credentials_exception
    
    # Chercher l'utilisateur en BDD
    user = db.query(User).filter(User.username == token_data.username).first()
    
    if user is None:
        raise credentials_exception
    
    # Vérifier que le compte est actif
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Compte désactivé"
        )
    
    return user

# ============================================================================
# DEPENDENCY: VÉRIFIER QUE L'UTILISATEUR EST ADMIN
# ============================================================================

async def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """
    Dependency qui vérifie que l'utilisateur connecté est ADMIN.
    
    Utilisée pour protéger les routes réservées aux administrateurs.
    
    Args:
        current_user: Utilisateur connecté (injecté par get_current_user)
    
    Returns:
        User: L'utilisateur admin
    
    Raises:
        HTTPException 403: Si l'utilisateur n'est pas admin
    
    Usage dans un endpoint:
        @app.delete("/admin/users/{user_id}")
        def delete_user(
            user_id: int,
            admin: User = Depends(require_admin)  # Seuls les admins peuvent accéder
        ):
            # ...
    """
    if current_user.role != Role.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Accès réservé aux administrateurs"
        )
    
    return current_user

# ============================================================================
# DEPENDENCY OPTIONNELLE: UTILISATEUR OU ANONYME
# ============================================================================

async def get_current_user_optional(
    credentials: HTTPAuthorizationCredentials | None = Depends(HTTPBearer(auto_error=False)),
    db: Session = Depends(get_db)
) -> User | None:
    """
    Dependency qui récupère l'utilisateur connecté s'il existe.
    
    Contrairement à get_current_user, cette dependency ne lève pas
    d'exception si l'utilisateur n'est pas connecté.
    
    Utilisée pour les routes qui ont un comportement différent
    selon que l'utilisateur est connecté ou non.
    
    Args:
        credentials: Token Bearer (optionnel)
        db: Session BDD
    
    Returns:
        User | None: L'utilisateur connecté ou None
    
    Usage:
        @app.get("/items")
        def list_items(user: User | None = Depends(get_current_user_optional)):
            if user:
                # Afficher les items de l'utilisateur
            else:
                # Afficher les items publics
    """
    if credentials is None:
        return None
    
    token = credentials.credentials
    token_data = decode_access_token(token)
    
    if token_data is None or token_data.username is None:
        return None
    
    user = db.query(User).filter(User.username == token_data.username).first()
    
    if user is None or not user.is_active:
        return None
    
    return user
