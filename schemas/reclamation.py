from pydantic import BaseModel, Field
from datetime import date
from models.reclamation import StatutReclamation  


class ReclamationBase(BaseModel):
    """
    Schéma de base pour une réclamation.
    Contient les champs communs à tous les schémas de réclamation.
    
    Attributes:
        sujet: Sujet de la réclamation
        description: Description détaillée
        date_creation: Date de création
        statut: Statut ouverte/en_cours/resolue (défaut: ouverte)
    """
    sujet: str = Field(..., min_length=1, max_length=100, description="Sujet de la réclamation (ex: Problème de facturation)")   
    description: str = Field(..., min_length=1, max_length=500, description="Description détaillée de la réclamation")   
    date_creation: date = Field(..., description="Date de création de la réclamation")   
    statut: str = Field(default="ouverte", description="Statut de la réclamation (ouverte, en_cours, resolue)")

class ReclamationCreate(ReclamationBase):
    """
    Schéma pour la création d'une réclamation.
    Le client_id est passé dans l'URL, pas dans le body.
    
    Utilisé pour POST /clients/{client_id}/reclamations
    
    Example:
        {
            "sujet": "Problème de facturation",
            "description": "Je n'ai pas reçu ma facture du mois dernier.",
            "date_creation": "2024-02-20",
            "statut": "ouverte"
        }
    """
    pass

class ReclamationResponse(ReclamationBase):
    """
    Schéma pour retourner une réclamation.
    Ajoute l'id et le client_id.
    
    Utilisé pour les réponses GET
    
    Example:
        {
            "id": 1,
            "sujet": "Problème de facturation",
            "description": "Je n'ai pas reçu ma facture du mois dernier.",
            "date_creation": "2024-02-20",
            "statut": "ouverte",
            "client_id": 1
        }
    """
    id: int = Field(..., description="Identifiant unique de la réclamation")
    client_id: int = Field(..., description="ID du client propriétaire")
    
    class Config:
        # Permet de convertir un objet SQLAlchemy en JSON
        from_attributes = True
    
class ReclamationUpdate(BaseModel):
    """
    Schéma pour la mise à jour partielle d'une réclamation.
    Tous les champs sont optionnels.
    
    Utilisé pour PATCH /reclamations/{reclamation_id}
    
    Example:
        {
            "statut": "en_cours"
        }
    """
    statut: StatutReclamation = Field(
        ...,
        description="Nouveau statut de la réclamation (ouverte, en_cours, resolue)"
    )