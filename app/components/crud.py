# import
from sqlalchemy.sql import func
from components.models import Client, DonnePersonnel, Commande, Produit, Promotion, Age, Region
from sqlalchemy.orm import Session


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
