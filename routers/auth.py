from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models.user import User
from schemas.user import UserCreate, UserResponse, LoginRequest, Token
from auth.utils import hash_password, verify_password
from auth.jwt import create_access_token
from auth.dependencies import get_current_user
# ============================================================================
# ROUTEUR AUTHENTIFICATION
# ============================================================================

router = APIRouter(
    prefix="/auth",
    tags=["Authentification"]
)

# ============================================================================
# INSCRIPTION (REGISTER)
# ============================================================================

@router.post("/register", response_model=UserResponse, status_code=201)
def register(user: UserCreate, db: Session = Depends(get_db)):
    """
    Crée un nouveau compte utilisateur.
    
    Le mot de passe est automatiquement hashé avant d'être stocké.
    
    Args:
        user: Données du nouvel utilisateur (username, email, password, role)
        db: Session BDD
    
    Returns:
        UserResponse: L'utilisateur créé (sans le mot de passe)
    
    Raises:
        HTTPException 400: Si le username ou l'email existe déjà
    
    Example:
        POST /auth/register
        {
            "username": "john",
            "email": "john@example.com",
            "password": "secret123",
            "role": "user"
        }
    """
    # Vérifier que le username n'existe pas déjà
    existing_user = db.query(User).filter(User.username == user.username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ce nom d'utilisateur existe déjà"
        )
    
    # Vérifier que l'email n'existe pas déjà
    existing_email = db.query(User).filter(User.email == user.email).first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cet email est déjà utilisé"
        )
    
    # Créer l'utilisateur avec le mot de passe hashé
    db_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hash_password(user.password),  # Hash le mot de passe
        role=user.role,
        is_active=1
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user

# ============================================================================
# CONNEXION (LOGIN)
# ============================================================================

@router.post("/login", response_model=Token)
def login(credentials: LoginRequest, db: Session = Depends(get_db)):
    """
    Connecte un utilisateur et retourne un token JWT.
    
    Processus:
        1. Cherche l'utilisateur par username
        2. Vérifie le mot de passe
        3. Génère un token JWT contenant username et role
        4. Retourne le token
    
    Args:
        credentials: Username et password
        db: Session BDD
    
    Returns:
        Token: Token JWT à utiliser pour les requêtes authentifiées
    
    Raises:
        HTTPException 401: Si les identifiants sont incorrects
    
    Example:
        POST /auth/login
        {
            "username": "ali",
            "password": "secret123"
        }
        
        Response:
        {
            "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
            "token_type": "bearer"
        }
    """
    # Chercher l'utilisateur
    user = db.query(User).filter(User.username == credentials.username).first()
    
    # Vérifier que l'utilisateur existe et que le mot de passe est correct
    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Identifiants incorrects",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Vérifier que le compte est actif
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Compte désactivé"
        )
    
    # Créer le token JWT avec username et role
    access_token = create_access_token(
        data={
            "sub": user.username,  # "sub" = subject (username)
            "role": user.role.value  # Ajouter le rôle au token
        }
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

# ============================================================================
# PROFIL DE L'UTILISATEUR CONNECTÉ
# ============================================================================

@router.get("/me", response_model=UserResponse)
def get_current_user_profile(current_user: User = Depends(get_current_user)):
    """
    Récupère le profil de l'utilisateur actuellement connecté.
    
    Route protégée : nécessite un token JWT valide.
    
    Args:
        current_user: Utilisateur connecté (injecté automatiquement)
    
    Returns:
        UserResponse: Profil de l'utilisateur
    
    Example:
        GET /auth/me
        Headers: Authorization: Bearer <token>
        
        Response:
        {
            "id": 1,
            "username": "john",
            "email": "john@example.com",
            "role": "user",
            "is_active": true
        }
    """
    return current_user
