from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from database import Base

class Client(Base): 
    # Nom de la table dans MySQL
    __tablename__ = "clients"
    
    # ========== COLONNES ==========
    id = Column(Integer, primary_key=True, index=True)  
    nom = Column(String(100), unique=True, nullable=False)  
    email = Column(String(100), unique=True, nullable=False)
    telephone = Column(String(20), nullable=True )
    
    # ========== RELATIONS ========== 
    # Relation One-to-Many avec Facture
    factures = relationship("Facture", back_populates="client", cascade="all, delete-orphan")
    # ✅ AJOUTE ÇA
    reclamations = relationship("Reclamation", back_populates="client", cascade="all, delete-orphan")

    # Explication du cascade:
    # - "all" : propage toutes les opérations (save, update, delete, etc.)
    # - "delete-orphan" : supprime les factures qui n'ont plus de client
    
    def __repr__(self):
        """Représentation textuelle du client (pour le debug)"""
        return f"<Client(id={self.id}, nom='{self.nom}', email='{self.email}')>"
