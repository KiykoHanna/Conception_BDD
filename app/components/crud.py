# import

from components.models import Client, DonnePersonnel, Commande, Produit, Promotion, Age, Region
from sqlalchemy.orm import Session


# Function pour creater un Client, DonnePersonnel, Commande, Produit, Promotion
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
    
