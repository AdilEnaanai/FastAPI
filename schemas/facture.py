from pydantic import BaseModel, Field
from datetime import date
from models.facture import StatutFacture

class FactureBase(BaseModel):
    """
    Schéma de base pour une facture.
    Contient les champs communs à tous les schémas de facture.
    
    Attributes:
        numero: Numéro unique de facture
        montant: Montant en euros (doit être > 0)
        date_emission: Date d'émission
        statut: Statut payé/impayé (défaut: impayé)
    """
    numero: str = Field(...,min_length=1,max_length=50,description="Numéro unique de facture (ex: FACT-001)")   
    montant: float = Field(...,gt=0, description="Montant de la facture en euros" )   
    date_emission: date = Field(...,description="Date d'émission de la facture")   
    statut: StatutFacture = Field(default=StatutFacture.IMPAYE, description="Statut de la facture (payé ou impayé)")

class FactureCreate(FactureBase):
    """
    Schéma pour la création d'une facture.
    Le client_id est passé dans l'URL, pas dans le body.
    
    Utilisé pour POST /clients/{client_id}/factures
    
    Example:
        {
            "numero": "FACT-001",
            "montant": 1500.50,
            "date_emission": "2024-01-15",
            "statut": "impayé"
        }
    """
    pass

class FactureResponse(FactureBase):
    """
    Schéma pour retourner une facture.
    Ajoute l'id et le client_id.
    
    Utilisé pour les réponses GET
    
    Example:
        {
            "id": 1,
            "numero": "FACT-001",
            "montant": 1500.50,
            "date_emission": "2024-01-15",
            "statut": "impayé",
            "client_id": 1
        }
    """
    id: int = Field(..., description="Identifiant unique de la facture")
    client_id: int = Field(..., description="ID du client propriétaire")
    
    class Config:
        # Permet de convertir un objet SQLAlchemy en JSON
        from_attributes = True

class FactureUpdate(BaseModel):
    """
    Schéma pour modifier uniquement le statut d'une facture.
    
    Utilisé pour PATCH /factures/{facture_id}
    
    Example:
        {
            "statut": "payé"
        }
    """
    statut: StatutFacture = Field(
        ...,
        description="Nouveau statut de la facture"
    )
