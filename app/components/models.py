# import
from sqlalchemy import Column, Integer, String, ForeignKey, create_engine
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

# Creation structure de base
Base = declarative_base()

#Client
class Age(Base):
    __tablename__ = "ages"
    age_id = Column(Integer, primary_key=True)
    age_plage = Column(String)
    # relationship
    clients = relationship("Client", back_populates="age")

class Region(Base):
    __tablename__ = "regions"
    region_id = Column(Integer, primary_key=True)
    region_nom = Column(String)
    # relationship
    clients = relationship("Client", back_populates="region")

class DonnePersonnel(Base):
    __tablename__ = "donnes_personnels"
    client_id = Column(Integer,ForeignKey("clients.client_id"), primary_key=True)
    login = Column(String)
    mot_de_passe = Column(String)
    # relationship
    client = relationship("Client", back_populates="donnes")

class Client(Base):
    __tablename__ = "clients"
    client_id = Column(Integer, primary_key=True)
    age_id = Column(Integer, ForeignKey("ages.age_id"))
    region_id = Column(Integer, ForeignKey("regions.region_id"))
    # relation
    age = relationship("Age", back_populates="clients")
    region = relationship("Region", back_populates="clients")
    donnes = relationship("DonnePersonnel", back_populates="client", uselist=False)
    commandes = relationship("Commande", back_populates="client")

#Produit

class Platform(Base):
    __tablename__ = "platforms"
    platform_cod = Column(Integer, primary_key=True)
    platform_nom = Column(String)
    # relationship
    produits = relationship("Produit", back_populates="platform")

class Genre(Base):
    __tablename__ = "genres"
    genre_cod = Column(Integer, primary_key=True)
    genre_nom = Column(String)
    # relationship
    produits = relationship("Produit", back_populates="genre")

class Publisher(Base):
    __tablename__ = "publishers"
    publisher_cod = Column(Integer, primary_key=True)
    publisher_nom = Column(String)
    # relationship
    produits = relationship("Produit", back_populates="publisher")

class Year(Base):
    __tablename__ = "years"
    year_cod = Column(Integer, primary_key=True)
    year_nom = Column(String)
    # relationship
    produits = relationship("Produit", back_populates="year")


class Produit(Base):
    __tablename__ = "produits"
    produit_id = Column(Integer, primary_key=True)
    name = Column(String)
    prix = Column(Integer)
    year_n = Column(Integer, ForeignKey("years.year_cod"))
    platform_cod = Column(Integer, ForeignKey("platforms.platform_cod"))
    genre_cod = Column(Integer, ForeignKey("genres.genre_cod"))
    publisher_cod = Column(Integer, ForeignKey("publishers.publisher_cod"))
    # relations
    year = relationship("Year", back_populates="produits")
    platform = relationship("Platform", back_populates="produits")
    genre = relationship("Genre", back_populates="produits")
    publisher = relationship("Publisher", back_populates="produits")
    commande = relationship("Commande", back_populates="produit")

# Commande

class Commande(Base):
    __tablename__ = "commandes"
    commande_id = Column(Integer, primary_key=True)
    nb_produit = Column(Integer)
    client_id = Column(Integer, ForeignKey("clients.client_id"))
    produit_id = Column(Integer, ForeignKey("produits.produit_id"))
    #relations
    client = relationship("Client", back_populates="commandes")
    produit = relationship("Produit", back_populates="commande")

