from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, extract

# Import de la configuration BDD
from database import engine, Base, get_db

# Import des modèles SQLAlchemy
from models import Client, Facture, StatutFacture,Reclamation

# Import des schémas Pydantic

from schemas import (
    ClientCreate,
    ClientResponse,
    ClientWithFactures,
    ClientWithReclamation,
    FactureCreate,
    FactureResponse,
    FactureUpdate,
)
from schemas.reclamation import ReclamationCreate, ReclamationResponse

# ============================================================================
# INITIALISATION
# ============================================================================

# Créer toutes les tables dans MySQL si elles n'existent pas
Base.metadata.create_all(bind=engine)

# Créer l'application FastAPI
app = FastAPI(
    title="API Gestion Clients & Factures",
    description="API pour gérer des clients et leurs factures",
    version="1.0.0"
)

# ============================================================================
# 1️⃣ CRÉER UN NOUVEAU CLIENT
# ============================================================================

@app.post("/clients", response_model=ClientResponse, status_code=201)
def creer_client(client: ClientCreate, db: Session = Depends(get_db)):
    """
    Crée un nouveau client dans la base de données.
    
    Args:
        client (ClientCreate): Données du client (nom, email, téléphone)
        db (Session): Session BDD injectée automatiquement par FastAPI
    
    Returns:
        ClientResponse: Le client créé avec son ID auto-généré
    
    Raises:
        HTTPException 400: Si l'email ou le nom existe déjà (contrainte UNIQUE)
    
    SQL généré:
        INSERT INTO clients (nom, email, telephone) 
        VALUES ('Jean Dupont', 'jean@example.com', '0612345678');
    """
    # Convertir le schéma Pydantic en dictionnaire
    # puis créer un objet SQLAlchemy Client
    db_client = Client(**client.model_dump())
    
    # Ajouter à la session (prépare l'INSERT)
    db.add(db_client)
    
    # Valider la transaction (exécute réellement l'INSERT)
    db.commit()
    
    # Rafraîchir l'objet pour récupérer l'ID auto-généré
    db.refresh(db_client)
    
    # Retourner le client (Pydantic le convertit en JSON)
    return db_client

# ============================================================================
# 2️⃣ RÉCUPÉRER TOUS LES CLIENTS
# ============================================================================

@app.get("/clients", response_model=list[ClientResponse])
def lire_clients(
    skip: int = 0,      # Pagination: nombre d'éléments à sauter
    limit: int = 100,   # Pagination: nombre max d'éléments à retourner
    db: Session = Depends(get_db)
):
    """
    Récupère la liste de tous les clients avec pagination.
    
    Args:
        skip: Nombre de clients à sauter (défaut: 0)
        limit: Nombre maximum de clients à retourner (défaut: 100)
        db: Session BDD
    
    Returns:
        list[ClientResponse]: Liste des clients
    
    SQL généré:
        SELECT * FROM clients LIMIT 100 OFFSET 0;
    
    Examples:
        GET /clients          → Retourne les 100 premiers clients
        GET /clients?skip=10&limit=5  → Retourne 5 clients à partir du 11ème
    """
    # Query = SELECT * FROM clients
    # .offset(skip) = OFFSET skip
    # .limit(limit) = LIMIT limit
    clients = db.query(Client).offset(skip).limit(limit).all()
    
    return clients

# ============================================================================
# 3️⃣ RÉCUPÉRER UN CLIENT PAR ID
# ============================================================================

@app.get("/clients/{client_id}", response_model=ClientResponse)
def lire_client(client_id: int, db: Session = Depends(get_db)):
    """
    Récupère un client spécifique par son ID.
    
    Args:
        client_id: ID du client recherché
        db: Session BDD
    
    Returns:
        ClientResponse: Le client trouvé
    
    Raises:
        HTTPException 404: Si le client n'existe pas
    
    SQL généré:
        SELECT * FROM clients WHERE id = 1 LIMIT 1;
    """
    # .filter() = WHERE
    # .first() = LIMIT 1 et retourne None si pas trouvé
    client = db.query(Client).filter(Client.id == client_id).first()
    
    if not client:
        raise HTTPException(
            status_code=404,
            detail=f"Client avec l'ID {client_id} non trouvé"
        )
    
    return client

# ============================================================================
# 4️⃣ SUPPRIMER UN CLIENT
# ============================================================================

@app.delete("/clients/{client_id}", status_code=204)
def supprimer_client(client_id: int, db: Session = Depends(get_db)):
    """
    Supprime un client et toutes ses factures associées.
    
    Grâce au cascade défini dans le modèle Client, toutes les factures
    du client sont automatiquement supprimées.
    
    Args:
        client_id: ID du client à supprimer
        db: Session BDD
    
    Returns:
        None (status 204 No Content)
    
    Raises:
        HTTPException 404: Si le client n'existe pas
    
    SQL généré:
        DELETE FROM factures WHERE client_id = 1;  -- Grâce au cascade
        DELETE FROM clients WHERE id = 1;
    """
    # Chercher le client
    client = db.query(Client).filter(Client.id == client_id).first()
    
    if not client:
        raise HTTPException(
            status_code=404,
            detail=f"Client avec l'ID {client_id} non trouvé"
        )
    
    # Supprimer le client (et ses factures grâce au cascade)
    db.delete(client)
    db.commit()
    
    # 204 No Content : pas de body dans la réponse
    return None

# ============================================================================
# 6️⃣ RÉCUPÉRER TOUTES LES FACTURES D'UN CLIENT
# ============================================================================

@app.get("/clients/{client_id}/factures", response_model=ClientWithFactures)
def lire_factures_client(client_id: int, db: Session = Depends(get_db)):
    """
    Récupère un client avec toutes ses factures.
    
    SQLAlchemy charge automatiquement les factures grâce à la relation
    définie dans le modèle Client (attribut 'factures').
    
    Args:
        client_id: ID du client
        db: Session BDD
    
    Returns:
        ClientWithFactures: Client avec sa liste de factures
    
    Raises:
        HTTPException 404: Si le client n'existe pas
    
    SQL généré:
        SELECT * FROM clients WHERE id = 1;
        SELECT * FROM factures WHERE client_id = 1;  -- Chargé automatiquement
    """
    client = db.query(Client).filter(Client.id == client_id).first()
    
    if not client:
        raise HTTPException(
            status_code=404,
            detail=f"Client avec l'ID {client_id} non trouvé"
        )
    
    # client.factures est automatiquement chargé grâce à la relation
    # Pydantic convertit le tout en JSON
    return client

# ============================================================================
# 7️⃣ AJOUTER UNE FACTURE À UN CLIENT
# ============================================================================

@app.post(
    "/clients/{client_id}/factures",
    response_model=FactureResponse,
    status_code=201
)
def creer_facture(
    client_id: int,
    facture: FactureCreate,
    db: Session = Depends(get_db)
):
    """
    Crée une nouvelle facture pour un client existant.
    
    Args:
        client_id: ID du client propriétaire
        facture: Données de la facture (numero, montant, date, statut)
        db: Session BDD
    
    Returns:
        FactureResponse: La facture créée
    
    Raises:
        HTTPException 404: Si le client n'existe pas
        HTTPException 400: Si le numéro de facture existe déjà
    
    SQL généré:
        SELECT * FROM clients WHERE id = 1;  -- Vérification
        INSERT INTO factures (numero, montant, date_emission, statut, client_id)
        VALUES ('FACT-001', 1500.50, '2024-01-15', 'impayé', 1);
    """
    # Vérifier que le client existe
    client = db.query(Client).filter(Client.id == client_id).first()
    
    if not client:
        raise HTTPException(
            status_code=404,
            detail=f"Client avec l'ID {client_id} non trouvé"
        )
    
    # Créer la facture avec le client_id
    # **facture.model_dump() : décompresse le dictionnaire en paramètres
    db_facture = Facture(**facture.model_dump(), client_id=client_id)
    
    db.add(db_facture)
    db.commit()
    db.refresh(db_facture)
    
    return db_facture

# ============================================================================
# 8️⃣ MODIFIER LE STATUT D'UNE FACTURE
# ============================================================================

@app.patch("/factures/{facture_id}", response_model=FactureResponse)
def modifier_statut_facture(
    facture_id: int,
    update: FactureUpdate,
    db: Session = Depends(get_db)
):
    """
    Modifie uniquement le statut d'une facture (impayé ↔ payé).
    
    PATCH est utilisé car on modifie partiellement la ressource
    (seulement le statut, pas tous les champs).
    
    Args:
        facture_id: ID de la facture à modifier
        update: Nouveau statut
        db: Session BDD
    
    Returns:
        FactureResponse: La facture mise à jour
    
    Raises:
        HTTPException 404: Si la facture n'existe pas
    
    SQL généré:
        SELECT * FROM factures WHERE id = 1;
        UPDATE factures SET statut = 'payé' WHERE id = 1;
    """
    # Chercher la facture
    facture = db.query(Facture).filter(Facture.id == facture_id).first()
    
    if not facture:
        raise HTTPException(
            status_code=404,
            detail=f"Facture avec l'ID {facture_id} non trouvée"
        )
    
    # Modifier uniquement le statut
    facture.statut = update.statut
    
    db.commit()
    db.refresh(facture)
    
    return facture

# ============================================================================
# 9️⃣ STATISTIQUES : FACTURES IMPAYÉES PAR MOIS
# ============================================================================

@app.get("/stats/factures-impayees")
def factures_impayees_par_mois(db: Session = Depends(get_db)):
    """
    Calcule le nombre de factures impayées groupées par mois.
    
    Utilise les fonctions d'agrégation SQL pour regrouper et compter.
    
    Args:
        db: Session BDD
    
    Returns:
        list[dict]: Liste de statistiques par mois
        
    Example de résultat:
        [
            {"annee": 2024, "mois": 1, "nombre_factures": 5},
            {"annee": 2024, "mois": 2, "nombre_factures": 3},
            {"annee": 2024, "mois": 12, "nombre_factures": 7}
        ]
    
    SQL généré:
        SELECT 
            YEAR(date_emission) as annee,
            MONTH(date_emission) as mois,
            COUNT(*) as nombre_factures
        FROM factures
        WHERE statut = 'impayé'
        GROUP BY annee, mois
        ORDER BY annee, mois;
    """
    # Construction de la requête SQL avec SQLAlchemy
    resultats = db.query(
        # extract('year', ...) = YEAR(date_emission)
        extract('year', Facture.date_emission).label('annee'),
        
        # extract('month', ...) = MONTH(date_emission)
        extract('month', Facture.date_emission).label('mois'),
        
        # func.count() = COUNT(*)
        func.count(Facture.id).label('nombre_factures')
    ).filter(
        # WHERE statut = 'impayé'
        Facture.statut == StatutFacture.IMPAYE
    ).group_by(
        # GROUP BY annee, mois
        'annee', 'mois'
    ).order_by(
        # ORDER BY annee, mois
        'annee', 'mois'
    ).all()
    
    # Convertir les résultats en liste de dictionnaires
    # r.annee, r.mois proviennent des .label() plus haut
    return [
        {
            "annee": int(r.annee),
            "mois": int(r.mois),
            "nombre_factures": r.nombre_factures
        }
        for r in resultats
    ]

# ============================================================================
# ENDPOINT DE SANTÉ (OPTIONNEL)
# ============================================================================

@app.get("/")
def root():
    """
    Endpoint racine pour vérifier que l'API fonctionne.
    """
    return {
        "message": "API Clients & Factures",
        "version": "1.0.0",
        "docs": "/docs"
    }

# ============================================================================
# ENDPOINT DE RECLAMATIONS (À AJOUTER)
# ============================================================================

@app.post(
    "/clients/{client_id}/reclamations",
    response_model=ReclamationResponse,
    status_code=201
)
def creer_reclamation(
    client_id: int,
    reclamation: ReclamationCreate,
    db: Session = Depends(get_db)
):
    """
    Crée une nouvelle réclamation pour un client existant.
    
    Args:
        client_id: ID du client propriétaire
        reclamation: Données de la réclamation (sujet, description, date_creation, statut)
        db: Session BDD
    
    Returns:
        ReclamationResponse: La réclamation créée
    
    Raises:
        HTTPException 404: Si le client n'existe pas
    
    SQL généré:
        SELECT * FROM clients WHERE id = 1;  -- Vérification
        INSERT INTO reclamations (sujet, description, date_creation, statut, client_id)
        VALUES ('Problème de facturation', 'Je n\'ai pas reçu ma facture du mois dernier.', '2024-02-20', 'ouverte', 1);
    """
    # Vérifier que le client existe
    client = db.query(Client).filter(Client.id == client_id).first()
    
    if not client:
        raise HTTPException(
            status_code=404,
            detail=f"Client avec l'ID {client_id} non trouvé"
        )
    
    # Créer la réclamation avec le client_id
    db_reclamation = Reclamation(**reclamation.model_dump(), client_id=client_id)
    
    db.add(db_reclamation)
    db.commit()
    db.refresh(db_reclamation)
    
    return db_reclamation

# ============================================================================
# ENDPOINT DE RECUPERER RECLAMATIONS 
# ============================================================================

@app.get("/clients/{client_id}/reclamations", response_model=ClientWithReclamation)
def lire_reclamation_client(client_id: int, db: Session = Depends(get_db)):
    """
    Récupère un client avec toutes ses reclamations.
    
    SQLAlchemy charge automatiquement les factures grâce à la relation
    définie dans le modèle Client (attribut 'reclamations').
    
    Args:
        client_id: ID du client
        db: Session BDD
    
    Returns:
        ClientWithReclamations: Client avec sa liste de reclamations
    
    Raises:
        HTTPException 404: Si le client n'existe pas
    
    SQL généré:
        SELECT * FROM clients WHERE id = 1;
        SELECT * FROM reclamations WHERE client_id = 1;  -- Chargé automatiquement
    """
    client = db.query(Client).filter(Client.id == client_id).first()
    
    if not client:
        raise HTTPException(
            status_code=404,
            detail=f"Client avec l'ID {client_id} non trouvé"
        )
    
    # client.factures est automatiquement chargé grâce à la relation
    # Pydantic convertit le tout en JSON
    return client

# ============================================================================
# 8️⃣ MODIFIER LE STATUT D'UNE RECLAMATION
# ============================================================================

@app.patch("/reclamations/{reclamation_id}", response_model=ReclamationResponse)
def modifier_statut_reclamation(
    reclamation_id: int,
    update: FactureUpdate,
    db: Session = Depends(get_db)
):
    """
    Modifie uniquement le statut d'une facture (impayé ↔ payé).
    
    PATCH est utilisé car on modifie partiellement la ressource
    (seulement le statut, pas tous les champs).
    
    Args:
        facture_id: ID de la facture à modifier
        update: Nouveau statut
        db: Session BDD
    
    Returns:
        FactureResponse: La facture mise à jour
    
    Raises:
        HTTPException 404: Si la facture n'existe pas
    
    SQL généré:
        SELECT * FROM factures WHERE id = 1;
        UPDATE factures SET statut = 'payé' WHERE id = 1;
    """
    # Chercher la facture
    reclamation = db.query(Reclamation).filter(Reclamation.id == reclamation_id).first()
    
    if not reclamation:
        raise HTTPException(
            status_code=404,
            detail=f"Facture avec l'ID {reclamation_id} non trouvée"
        )
    
    # Modifier uniquement le statut
    reclamation.statut = update.statut
    
    db.commit()
    db.refresh(reclamation)
    
    return reclamation
