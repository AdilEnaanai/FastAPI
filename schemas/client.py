from pydantic import BaseModel, EmailStr, Field

from schemas.reclamation import ReclamationResponse

class ClientBase(BaseModel):
    """
    Schéma de base pour un client.
    Contient les champs communs à tous les schémas de client.
    
    Attributes:
        nom: Nom du client (2-100 caractères)
        email: Email valide (validation automatique par EmailStr)
        telephone: Numéro de téléphone optionnel
    """
    nom: str = Field(...,min_length=2,max_length=100,description="Nom complet du client")
    email: EmailStr = Field(...,description="Adresse email valide")
    telephone: str | None = Field(default=None, max_length=20,description="Numéro de téléphone (optionnel)")

class ClientCreate(ClientBase):
    """
    Schéma pour la création d'un client.
    Hérite de ClientBase sans ajouter de champs.
    
    Utilisé pour valider les données lors du POST /clients
    
    Example:
        {
            "nom": "Jean Dupont",
            "email": "jean@example.com",
            "telephone": "0612345678"
        }
    """
    pass

class ClientResponse(ClientBase):
    """
    Schéma pour retourner un client.
    Ajoute l'id généré par la base de données.
    
    Utilisé pour les réponses GET /clients
    
    Example:
        {
            "id": 1,
            "nom": "Jean Dupont",
            "email": "jean@example.com",
            "telephone": "0612345678"
        }
    """
    id: int = Field(..., description="Identifiant unique du client")
    
    class Config:
        # Permet de convertir un objet SQLAlchemy en JSON
        # Anciennement "orm_mode = True" dans Pydantic v1
        from_attributes = True

class ClientWithFactures(ClientResponse):
    """
    Schéma pour retourner un client avec ses factures.
    Utilisé pour l'endpoint GET /clients/{id}/factures
    
    Example:
        {
            "id": 1,
            "nom": "Jean Dupont",
            "email": "jean@example.com",
            "telephone": "0612345678",
            "factures": [
                {
                    "id": 1,
                    "numero": "FACT-001",
                    "montant": 1500.50,
                    "date_emission": "2024-01-15",
                    "statut": "impayé",
                    "client_id": 1
                }
            ]
        }
    """
    # Import ici pour éviter les imports circulaires
    # (facture.py importe aussi client.py)
    factures: list["FactureResponse"] = Field(
        default_factory=list,  # Liste vide par défaut
        description="Liste des factures du client"
    )
    
    class Config:
        from_attributes = True

# Import nécessaire pour la validation des types forward-referenced
from .facture import FactureResponse
ClientWithFactures.model_rebuild()  # Reconstruit le modèle avec FactureResponse


class ClientWithReclamation(ClientResponse):
    # Import ici pour éviter les imports circulaires
    # (facture.py importe aussi client.py)
    reclamations: list["ReclamationResponse"] = Field(
        default_factory=list,  # Liste vide par défaut
        description="Liste des reclamations du client"
    )