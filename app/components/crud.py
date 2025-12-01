# import

from components.models import *

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, create_engine
from sqlalchemy.orm import relationship, declarative_base, sessionmaker
from sqlalchemy.sql import func

engine = create_engine("sqlite:///BD_Ventes_de_jeux_video.bd") 

# session
Session = sessionmaker(bind=engine)
session = Session()

def create_Client(age_id:int, region_id:int):
    """Create and persist a new Client in the database.

    Args:
        age_id (int): ID of the age category to assign to the client.
        region_id (int): ID of the region to assign to the client.

    Returns:
        Client: The newly created Client object.

    Raises:
        Exception: If the session commit fails. The session will be rolled back and the exception re-raised.
    """
    try:
        new_client = Client(
        age_id = age_id,
        region_id = region_id,
        )

        session.add(new_client)
        session.commit()
        return new_client
    except Exception as e:
        session.rollback()
        raise e
    
def create_donne_pers(client_id: int, login: str, mot_de_passe_hash: str):
    """Create and persist a DonnePersonnel linked to a Client.

    Args:
        client_id (int): ID of the Client to link.
        login (str): Login name.
        mot_de_passe_hash (str): Hashed password.

    Returns:
        DonnePersonnel: The newly created DonnePersonnel object.
    """
    try:
        session.add(DonnePersonnel(
            login = login,
            mot_de_passe_hash = mot_de_passe_hash,
            client_id = client_id,
            date_suppression = None,
            anonymise = False,
            ))
        session.commit()
    except Exception as e:
        session.rollback()
        raise e

def create_commande(client_id, produit_id, nb_produit):
    
    try:
        session.add(Commande(
            client_id = client_id,
            produit_id = produit_id,
            nb_produit = nb_produit,
            ))
        session.commit()
    except Exception as e:
        session.rollback()
        raise e