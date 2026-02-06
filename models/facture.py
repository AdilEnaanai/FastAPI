from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey, Enum
from sqlalchemy.orm import relationship
from database import Base
import enum

# ============================================================================
# ENUMÉRATION POUR LE STATUT
# ============================================================================

class StatutFacture(str, enum.Enum):
    """
    Énumération des statuts possibles d'une facture.
    
    Hérite de str pour être sérialisable en JSON facilement.
    
    Values:
        PAYE: La facture a été réglée
        IMPAYE: La facture est en attente de paiement
    """
    PAYE = "payé"
    IMPAYE = "impayé"

# ============================================================================
# MODÈLE FACTURE
# ============================================================================

class Facture(Base):
    # Nom de la table dans MySQL
    __tablename__ = "factures"
    
    # ========== COLONNES ==========   
    id = Column(Integer, primary_key=True, index=True)  # ID auto-incrémenté, indexé pour les recherches rapides
    numero = Column(String(50), unique=True, nullable=False)  # Numéro de facture unique et obligatoire)  
    montant = Column(Float, nullable=False)  # Montant de la facture, obligatoire   
    date_emission = Column(Date, nullable=False)  # Date d'émission de la facture, obligatoire  
    statut = Column(Enum(StatutFacture),default=StatutFacture.IMPAYE, nullable=False)  # Statut de la facture, par défaut "impayé"
    
    # ========== CLÉ ÉTRANGÈRE ==========
    client_id = Column(Integer,ForeignKey("clients.id"),nullable=False)  # ID du client lié à cette facture, obligatoire
    
    # ========== RELATIONS ==========
        # Relation Many-to-One avec Client
    client = relationship("Client",  back_populates="factures")  # Permet d'accéder au client depuis la facture
    
    def __repr__(self):
        """Représentation textuelle de la facture (pour le debug)"""
        return f"<Facture(id={self.id}, numero='{self.numero}', montant={self.montant}, statut='{self.statut.value}')>"
