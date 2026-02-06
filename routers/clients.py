from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Client
from models.user import User
from schemas import ClientCreate, ClientResponse
from auth.dependencies import get_current_user, require_admin

# ============================================================================
# ROUTEUR CLIENTS
# ============================================================================

router = APIRouter(
    prefix="/clients",
    tags=["Clients"]
)

# ============================================================================
# CRÉER UN CLIENT (USER ou ADMIN)
# ============================================================================

@router.post("", response_model=ClientResponse, status_code=201)
def creer_client(
    client: ClientCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)  # 🔒 Authentification requise
):
    """
    Crée un nouveau client.
    
    🔒 Route protégée : accessible par USER et ADMIN.
    
    Args:
        client: Données du client
        db: Session BDD
        current_user: Utilisateur connecté (vérifié automatiquement)
    
    Returns:
        ClientResponse: Le client créé
    """
    db_client = Client(**client.model_dump())
    db.add(db_client)
    db.commit()
    db.refresh(db_client)
    
    return db_client

# ============================================================================
# LIRE TOUS LES CLIENTS (USER ou ADMIN)
# ============================================================================

@router.get("", response_model=list[ClientResponse])
def lire_clients(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)  # 🔒 Authentification requise
):
    """
    Récupère tous les clients.
    
    🔒 Route protégée : accessible par USER et ADMIN.
    """
    clients = db.query(Client).offset(skip).limit(limit).all()
    return clients

# ============================================================================
# LIRE UN CLIENT (USER ou ADMIN)
# ============================================================================

@router.get("/{client_id}", response_model=ClientResponse)
def lire_client(
    client_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)  # 🔒 Authentification requise
):
    """
    Récupère un client spécifique.
    
    🔒 Route protégée : accessible par USER et ADMIN.
    """
    client = db.query(Client).filter(Client.id == client_id).first()
    
    if not client:
        raise HTTPException(status_code=404, detail="Client non trouvé")
    
    return client

# ============================================================================
# SUPPRIMER UN CLIENT (ADMIN UNIQUEMENT)
# ============================================================================

@router.delete("/{client_id}", status_code=204)
def supprimer_client(
    client_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)  # 🔒 ADMIN uniquement
):
    """
    Supprime un client.
    
    🔒 Route protégée : accessible par ADMIN UNIQUEMENT.
    
    Args:
        client_id: ID du client à supprimer
        db: Session BDD
        admin: Utilisateur admin (vérifié automatiquement)
    """
    client = db.query(Client).filter(Client.id == client_id).first()
    
    if not client:
        raise HTTPException(status_code=404, detail="Client non trouvé")
    
    db.delete(client)
    db.commit()
    
    return None
