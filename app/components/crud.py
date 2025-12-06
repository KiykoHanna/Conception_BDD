# import
from sqlalchemy.sql import func
from components.models import Log, Client, DonnePersonnel, Commande, Produit, Genre, Promotion, Age, Region, Platform, Publisher, Year
from sqlalchemy.orm import Session
import pandas as pd


# Function pour CREATE un Client, DonnePersonnel, Commande, Produit, Promotion
def create_client(session: Session, age_id:int, region_id:int):
    """Create and persist a new Client in the database.

    Args:
        age_id (int): ID of the age category for the client.
        region_id (int): ID of the region where the client belongs.

    Returns:
        Client: The newly created Client object.

    Raises:
        Exception: If the session commit fails, the transaction is rolled back and the exception is re-raised.
    """
    try:
        client = Client(
            age_id=age_id,
            region_id=region_id
        )
        session.add(client)
        session.commit()
        return client
    except Exception as e:
        session.rollback()
        raise e
    
def create_donne_personnel(session: Session, login, mot_de_passe_hash):
    """Create and persist a new DonnePersonnel (personal data) record for a client.

    Args:
        login (str): Login username for the personal data.
        mot_de_passe_hash (str): Hashed password.

    Returns:
        DonnePersonnel: The newly created DonnePersonnel object.

    Raises:
        Exception: If the session commit fails, the transaction is rolled back and the exception is re-raised.
    """
    try:
        donne = DonnePersonnel(
            login=login,
            mot_de_passe_hash=mot_de_passe_hash,
            date_suppression=None,
            anonymise=False
        )
        session.add(donne)
        session.commit()
        return donne
    except Exception as e:
        session.rollback()
        raise e

def create_commande(session: Session, client_id, produit_id, nb_produit):
    """Create and persist a new order (Commande) in the database, optionally applying a promotion.

    The function looks for a promotion associated with the given product — 
    if found, the order will reference the promotion; otherwise, no promotion is applied.

    Args:
        client_id (int): ID of the client placing the order.
        produit_id (int): ID of the product being ordered.
        nb_produit (int): Number of units ordered.

    Raises:
        Exception: If the session commit fails. The session will be rolled back and the exception re-raised.
    """
    try:
        promo = session.query(Promotion).filter(Promotion.produit_id=={produit_id}).first()
        promo_id = promo.promotion_id if promo else 0
        session.add(Commande(
            client_id = client_id,
            produit_id = produit_id,
            nb_produit = nb_produit,
            promotion_id = promo_id
            ))
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    
def create_promotion(session: Session, produit_id:int, promotion_percent:int, region_id_promo:int):
    """Create a promotion for a given product and link it to a region.

    Args:
        produit_id (int): ID of the product.
        promotion_percent (int): Discount percent.
        region_id_promo (int): ID of the region for this promotion.

    Raises:
        Exception: If commit fails, the session is rolled back and the exception re-raised.
    """
    try:
        region = session.query(Region).filter(Region.region_id==region_id_promo).first()

        obj = Promotion(
            produit_id = produit_id,
            promotion_percent = promotion_percent
        )
        obj.regions.append(region)
        session.add(obj)
        session.commit()
    except Exception as e:
        session.rollback()
        raise e

# READ

def read_table(session: Session, table_class, limit=None, filter_exp=None):
    """
    Lit une table SQLAlchemy et renvoie les résultats dans un DataFrame.

    Args:
        table_class: Modèle SQLAlchemy (ex.: Client, Commande).
        limit: Nombre maximum de lignes à retourner (optionnel).
        filter_exp: Expression SQLAlchemy pour filtrer (optionnel).

    Returns:
        DataFrame contenant le résultat de la requête.

    Raises:
        Exception: If commit fails, the session is rolled back and the exception re-raised.
    """

    try:
        query = session.query(table_class)
        
        if table_class is Client:
            query.update(
            {Client.date_derniere_utilisation: func.now()},
            synchronize_session=False
            )
            session.commit()

        if filter_exp is not None:
            query = query.filter(filter_exp)
        
        if limit is not None:
            query = query.limit(limit)
        
        df = pd.read_sql(query.statement, session.get_bind())
        return df
    
    except Exception as e:
        session.rollback()
        raise e


def read_promo(session: Session, limit=None, filter_exp=None):
    """Interroger les promotions avec les noms des produits et les régions associées.
    Cette fonction retourne un DataFrame contenant les promotions jointes aux produits,
    ainsi qu'une chaîne formatée listant les régions pour chaque promotion.

    Args:
        limit (int, optional): Nombre maximal de lignes à retourner.
        filter_exp (expression SQLAlchemy, optional): Expression de filtrage à appliquer.

    Returns:
        tuple:
            - pandas.DataFrame: Résultats de la requête avec Promotion et Produit.name.
            - str: Chaîne formatée listant les promotions et les régions associées.

    Raises:
        Exception: Toute exception levée pendant l'exécution de la requête est capturée et réémise.
    """

    try:
        query = (session.query(
            Promotion,
            Produit.name
            )).join(Produit, Produit.produit_id == Promotion.produit_id)
        
        if filter_exp is not None:
            query = query.filter(filter_exp)
        if limit is not None:
            query = query.limit(limit)

        df = pd.read_sql(query.statement, session.get_bind(), index_col="promotion_id")
        
        list_reg = ""
        for promo, prod_name in query:
            for reg in promo.regions:
                list_reg += f"{promo.promotion_percent}% apply to {prod_name}: region -- {reg.region_nom}\n"
        
        return df, list_reg
    
    except Exception as e:
        raise e

def read_produit(session: Session, limit=None, filter_exp=None):
    """Interroger les produits avec leurs informations détaillées.

    Cette fonction retourne un DataFrame contenant les produits et les informations
    associées provenant des tables liées : année, plateforme, genre et éditeur.

    Args:
        limit (int, optional): Nombre maximal de lignes à retourner.
        filter_exp (expression SQLAlchemy, optional): Expression de filtrage à appliquer.

    Returns:
        pandas.DataFrame: Résultats de la requête avec les détails des produits.

    Raises:
        Exception: Toute exception levée pendant l'exécution de la requête est réémise.
    """

    try:
        query = (
            session.query(
                Produit.produit_id, Produit.prix, Produit.name,
                Year.year_nom.label("year_nom"),
                Platform.platform_nom.label("platform_nom"),
                Genre.genre_nom.label("genre_nom"),
                Publisher.publisher_nom.label("publisher_nom")
            )
            .join(Year, Year.year_cod == Produit.year_n)
            .join(Platform, Platform.platform_cod == Produit.platform_cod)
            .join(Genre, Genre.genre_cod == Produit.genre_cod)
            .join(Publisher, Publisher.publisher_cod == Produit.publisher_cod)
        )
        
        if filter_exp is not None:
            query = query.filter(filter_exp)
        if limit is not None:
            query = query.limit(limit)
        
        df = pd.read_sql(query.statement, session.get_bind())

        return df
    except Exception as e:
        raise e


def read_command(session: Session, limit=None, filter_exp=None):
    """Interroger les commandes avec les informations sur le produit et la promotion.

    Cette fonction retourne un DataFrame contenant les commandes, le nombre de produits,
    le nom du produit et le pourcentage de promotion s'il existe.

    Args:
        limit (int, optional): Nombre maximal de lignes à retourner.
        filter_exp (expression SQLAlchemy, optional): Expression de filtrage à appliquer.

    Returns:
        pandas.DataFrame: Résultats de la requête avec les détails des commandes.

    Raises:
        Exception: Toute exception levée pendant l'exécution de la requête est réémise.
    """
     
    try:
        query = (session.query(
            Commande.commande_id,
            Commande.nb_produit,
            Commande.client_id,
            Produit.name.label("produit_nom"),
            Produit.prix.label("prix"),
            Promotion.promotion_percent,
            )
        .join(Produit, Produit.produit_id == Commande.produit_id)
        .outerjoin(Promotion, Promotion.produit_id == Commande.produit_id)
        )
        
        if filter_exp is not None:
            query = query.filter(filter_exp)
        if limit is not None:
            query = query.limit(limit)

        df = pd.read_sql(query.statement, session.get_bind())
        df["promotion_percent"] = df["promotion_percent"].fillna(0)
        df['prix total'] = df["nb_produit"] * df["prix"] * (1 - (0.01 * df["promotion_percent"]))
        return df
    
    except Exception as e:
        raise e

def read_client(session: Session, limit=None, filter_exp=None):
    """
    Récupère les informations des clients avec les données associées et le nombre de commandes.

    Args:
        limit (int, optional): Nombre maximum de clients à récupérer. Par défaut, None = tous.
        filter_exp (Expression, optional): Expression SQLAlchemy pour filtrer les clients.
                                           Exemple : Client.region_id == 0

    Behavior:
        - Joint les tables Age et Region pour récupérer les informations associées.
        - Calcule le nombre de commandes par client.
        - Applique un filtre et une limite si fournis.
        - Retourne le résultat sous forme de DataFrame pandas.

    Returns:
        pandas.DataFrame: Contient les colonnes suivantes :
            - client_id
            - age_plage
            - region_nom
            - Nb_commande
    """
    try:
        query = (
            (session.query(
            Client.client_id,
            Age.age_plage,
            Region.region_nom,
            func.count(Commande.commande_id).label("Nb_commande")
            ))
            .join(Commande, Commande.client_id == Client.client_id)
            .join(Age, Age.age_id == Client.age_id)
            .join(Region, Region.region_id == Client.region_id)
            ).group_by(Client.client_id)
        
        if filter_exp is not None:
            query = query.filter(filter_exp)
        
        if limit is not None:
            query = query.limit(limit)  

        
        df = pd.read_sql(query.statement, session.get_bind(), index_col="client_id")

        return df
    
    except Exception as e:
        raise e


# UPDATE

def update_table(session: Session, table_nom, data_id, **kwargs):
    """
    Met à jour les colonnes spécifiées d'un enregistrement dans une table SQLAlchemy.

    Args:
        table_nom (DeclarativeMeta): La classe SQLAlchemy représentant la table.
        data_id (int): L'identifiant de l'enregistrement à mettre à jour.
        **kwargs: Paires clé-valeur représentant les colonnes à modifier et leurs nouvelles valeurs.
                  Exemple : age_id=1, region_id=0

    Behavior spécifique:
        - Si la table est `Client`, la colonne `date_derniere_utilisation` sera mise à jour avec l'heure actuelle.

    Returns:
        None si l'objet avec `data_id` n'existe pas. Sinon, commit les changements dans la base de données.

    Exemple:
        update_table(Client, 51, age_id=1, region_id=0)
    """
    obj = session.get(table_nom, data_id)
    if not obj:
        return None
    
    for field, value in kwargs.items():
        setattr(obj, field, value)
    

    if table_nom is Client:
        obj.date_derniere_utilisation = func.now()
        
    session.commit()
    print(f"L’enregistrement dans {table_nom.__tablename__} a été renouvelé.")



# DELETE

def delete_objet(session: Session, table_nom, data_id):
    """
    Supprime un enregistrement spécifique d'une table SQLAlchemy.

    Args:
        table_nom (DeclarativeMeta): La classe SQLAlchemy représentant la table.
        data_id (int): L'identifiant de l'enregistrement à supprimer.

    Behavior:
        - Cherche l'objet dans la base via `session.get`.
        - Si l'objet existe, le supprime et commit la transaction.
        - Si l'objet n'existe pas, aucune suppression n'est effectuée.
        - Capture les exceptions et affiche un message d'erreur.

    Returns:
        None

    Exemple:
        delete_objet(Client, 51)
    """
    try:
        obj = session.get(table_nom, data_id)
        if obj is not None:
            session.delete(obj)
        session.commit()
    except Exception as e:
        print(e)

def delete_filtre(session: Session, table_nom, filter_exp):
    """
    Supprime tous les enregistrements d'une table SQLAlchemy correspondant à un filtre donné.

    Args:
        table_nom (DeclarativeMeta): La classe SQLAlchemy représentant la table.
        filter_exp: Expression de filtre SQLAlchemy pour sélectionner les enregistrements à supprimer.
                    Exemple : Client.age_id == 1

    Behavior:
        - Crée une requête avec `session.query(table_nom).filter(filter_exp)`.
        - Supprime tous les enregistrements filtrés via `.delete()`.
        - Capture les exceptions et affiche un message d'erreur.

    Returns:
        None

    Exemple:
        delete_filtre(Client, Client.age_id == 1)
    """
    try:
        query = session.query(table_nom).filter(filter_exp)
        query.delete(synchronize_session=False)
        session.commit()

    except Exception as e:
        print(e)

# LOGGING

def add_log(session: Session, type_action, table_cible, client_id=None, details=None):
    """Ajoute une entrée dans la table des logs.

    Args:
        session: session SQLAlchemy utilisée pour la connexion à la base de données
        type_action (str): type d'action ("INSERT", "UPDATE", "DELETE", etc.)
        table_cible (str): nom de la table concernée par l'action
        client_id (int, optionnel): identifiant du client ou de l'utilisateur effectuant l'action
        details (str, optionnel): informations complémentaires, par exemple au format JSON

    Raises:
        Exception: en cas d'erreur lors de l'insertion dans la table logs,
                   la transaction est annulée (rollback) et l'exception est levée.
    """
    
    try:
        log_entry = Log(
            type_action=type_action,
            table_cible=table_cible,
            client_id=client_id,
            details=details
        )
        session.add(log_entry)
        session.commit()
    except Exception as e:
        session.rollback()
        raise e