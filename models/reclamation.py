
import enum

from sqlalchemy import Column, Date, Enum, ForeignKey, Integer,String
from sqlalchemy.orm import relationship
from database import Base


class StatutReclamation(str,enum.Enum):
    """
    Énumération des statuts possibles d'une réclamation.
    
    Hérite de str pour être sérialisable en JSON facilement.
    
    Values:
        OUVERTE: La réclamation est ouverte
        EN_COURS: La réclamation est en cours de traitement
        RESOLUE: La réclamation a été résolue
    """
    OUVERTE = "ouverte"
    EN_COURS = "en_cours"
    RESOLUE = "resolue"
    

class Reclamation(Base):
    # Nom de la table dans MySQL
    __tablename__ = "reclamations"
    
    # ========== COLONNES ==========   
    id = Column(Integer, primary_key=True, index=True)  # ID auto-incrémenté, indexé pour les recherches rapides
    sujet=Column(String(100), nullable=False)  # Sujet de la réclamation, obligatoire
    description = Column(String(500), nullable=False)  # Description de la réclamation, obligatoire   
    date_creation = Column(Date, nullable=False)  # Date de création de la réclamation, obligatoire  
    statut = Column(Enum(StatutReclamation), default=StatutReclamation.OUVERTE, nullable=False)  # Statut de la réclamation, par défaut "ouverte"
    
    # ========== CLÉ ÉTRANGÈRE ==========
    client_id = Column(Integer,ForeignKey("clients.id"),nullable=False)  # ID du client lié à cette réclamation, obligatoire
    
    # ========== RELATIONS ==========
        # Relation Many-to-One avec Client
    client = relationship("Client",  back_populates="reclamations")  # Permet d'accéder au client depuis la réclamation
    
    def __repr__(self):
        """Représentation textuelle de la réclamation (pour le debug)"""
        return f"<Reclamation(id={self.id}, statut='{self.statut.value}', date_creation={self.date_creation})>"