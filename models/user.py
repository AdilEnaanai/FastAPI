from sqlalchemy import Column, Integer, String, Enum
from sqlalchemy.orm import relationship
from database import Base
import enum

# ============================================================================
# ENUM POUR LES RÔLES
# ============================================================================

class Role(str, enum.Enum):
    """
    Énumération des rôles utilisateurs.
    
    Values:
        ADMIN: Administrateur (accès total)
        USER: Utilisateur standard (accès limité)
    """
    ADMIN = "admin"
    USER = "user"

# ============================================================================
# MODÈLE USER
# ============================================================================

class User(Base):
    __tablename__ = "users"
    
    # ========== COLONNES ==========
    
    id = Column(Integer, primary_key=True, index=True)
    
    username = Column(String(50),unique=True,nullable=False,index=True)
    
    email = Column(String(100),unique=True,nullable=False)
    
    hashed_password = Column(String(255),nullable=False )
    
    role = Column(Enum(Role),default=Role.USER,nullable=False)
    
    is_active = Column(Integer,default=1,nullable=False)
    
    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', role='{self.role.value}')>"
