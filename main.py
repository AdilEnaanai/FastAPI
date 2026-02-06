from fastapi import FastAPI
from database import engine, Base

# Import des routeurs
from routers import auth, clients

# ============================================================================
# INITIALISATION
# ============================================================================

# Créer toutes les tables
Base.metadata.create_all(bind=engine)

# Créer l'application
app = FastAPI(
    title="API Gestion Clients & Factures",
    description="API avec authentification JWT et gestion des rôles",
    version="2.0.0"
)

# ============================================================================
# ENREGISTREMENT DES ROUTEURS
# ============================================================================

# Routes d'authentification (publiques)
app.include_router(auth.router)

# Routes clients (protégées)
app.include_router(clients.router)

# ============================================================================
# ENDPOINT RACINE
# ============================================================================

@app.get("/")
def root():
    """Endpoint racine public"""
    return {
        "message": "API Clients & Factures avec Authentification",
        "version": "2.0.0",
        "docs": "/docs",
        "endpoints": {
            "register": "/auth/register",
            "login": "/auth/login",
            "profile": "/auth/me (protégé)",
            "clients": "/clients (protégé)"
        }
    }
