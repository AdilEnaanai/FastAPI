"""
Package des modèles SQLAlchemy.
Facilite l'import des modèles depuis d'autres fichiers.
"""

from .client import Client
from .facture import Facture, StatutFacture
from .reclamation import Reclamation,StatutReclamation

# Permet d'importer directement : from models import Client, Facture
__all__ = ["Client", "Facture", "StatutFacture", "Reclamation", "StatutReclamation"]
