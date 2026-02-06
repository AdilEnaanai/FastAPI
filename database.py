from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

# Charger les variables d'environnement depuis le fichier .env
load_dotenv()

# Récupérer l'URL de connexion MySQL
DATABASE_URL = os.getenv("DATABASE_URL")

# Créer le moteur de base de données
# echo=True : affiche les requêtes SQL dans la console (utile pour le debug)
engine = create_engine(DATABASE_URL, echo=True)

# Créer une fabrique de sessions
# autocommit=False : les transactions doivent être validées manuellement
# autoflush=False : ne synchronise pas automatiquement avec la BDD
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Classe de base pour tous les modèles SQLAlchemy
Base = declarative_base()

# Dependency pour obtenir une session de base de données
def get_db():
    """
    Génère une session BDD pour chaque requête.
    La session est automatiquement fermée après utilisation.
    
    Yields:
        Session: Session SQLAlchemy active
    """
    db = SessionLocal()
    try:
        yield db  # Fournit la session à l'endpoint
    finally:
        db.close()  # Ferme toujours la session, même en cas d'erreur
