"""
Package des schémas Pydantic.
Facilite l'import des schémas depuis d'autres fichiers.
"""

from .client import ClientCreate, ClientResponse, ClientWithFactures,ClientWithReclamation
from .facture import FactureCreate, FactureResponse, FactureUpdate
from .reclamation import ReclamationCreate,ReclamationResponse,ReclamationUpdate

# Permet d'importer directement : from schemas import ClientCreate, FactureCreate
__all__ = [
    "ClientCreate",
    "ClientResponse",
    "ClientWithFactures",
    "ClientWithReclamation",
    "FactureCreate",
    "FactureResponse",
    "FactureUpdate",
    "ReclamationCreate",
    "ReclamationResponse",
    "ReclamationUpdate",
]
