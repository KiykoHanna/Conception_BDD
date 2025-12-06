# import

from IPython.display import clear_output
import json
import os

from sqlalchemy import  create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import func
from components.models import *           
from components.crud import *             


def menu_admin(session):
    """
    La fonction affiche un menu interactif destiné à l’administrateur.
    Elle permet d’exécuter différentes opérations sur les utilisateurs : création, lecture, mise à jour, suppression.
    La fonction utilise match/case pour gérer les choix de manière claire et structurée. 
    Elle inclut également une gestion d’erreurs afin d’éviter l’arrêt du programme en cas de saisie incorrecte ou d’exception.
    """
    try:
        while True:
            tables = {
                        "Commande": Commande,
                        "Client": Client,
                        "Promotion": Promotion,
                        "DonnePersonnel": DonnePersonnel,
                        "Produit": Produit
                    } 
            

            clear_output(wait=True)
            print("\n--- Menu ---")
            print("Fonctions possibles :")
            print("  c : créer ")
            print("  r : lire ")
            print("  u : mettre à jour ")
            print("  d : supprimer ")
       
            action = input("Choisissez une action (c/r/u/d) : ").strip().lower()
            clear_output(wait=True)
            match action:
                case "c":
                    creation_menu(session)
                case "r":
                    read_menu(session)
                case "u":
                    table_nom = input("Nom de la table : ").strip()
                    table_class = tables.get(table_nom)
                    data_id = int(input("ID: "))
                    raw_kwargs = input("kwargs (en JSON, ex: {\"name\": \"Alice\"}): ")

                    kwargs = json.loads(raw_kwargs) if raw_kwargs else {}

                    update_table(session, table_class, data_id, **kwargs)
                    add_log(session, "update", table_nom, details=f"data_id: {data_id}")
                case "d":
                    delete_menu(session)
                case _:
                    print("Erreur de saisie.")
                    continue

            # Continuer ou quitter
            choix = input("Continuer ? (c = continuer, e = exit) : ").strip().lower()

            match choix:
                case "c":
                    continue
                case "e":
                    break
                case _:
                    print("Erreur de saisie. Retour au menu.")

    except Exception as e:
        print(f"Erreur : {e}")

def creation_menu(session):
    try:
        while True:
            clear_output(wait=True)
            print("\n--- CREATION Menu ---")
            print("Fonctions possibles :")
            print("  a : create_client")
            print("  b : create_commande")
            print("  c : create_promotion")
            print("  q : quitter")

            action = input("Choisissez une action (a/b/c/q) : ").strip().lower()
            clear_output(wait=True)

            if action == "q":
                break

            match action:

                # --- A ---
                case "a":
                    login = input("login : ").strip()
                    mot_de_passe = input("mot_de_passe : ").strip()
                    mot_de_passe_hash = hash(mot_de_passe)
                    create_donne_personnel(session, login, mot_de_passe_hash)
                    age_id = int(input("age_id (1–4) : ").strip())
                    region_id = int(input("region_id (1–4) : ").strip())
                    create_client(session, age_id, region_id)
                    add_log(session, "create", "Client",  details=f"client_login: {login}")

                # --- B ---
                case "b":

                    client_id = input("client_id : ").strip()
                    produit_id = input("produit_id : ").strip()
                    nb_produit = input("nb_produit : ").strip()
                    create_commande(session, client_id, produit_id, nb_produit)
                    add_log(session, "create", "Commande")

                # --- C ---

                case "c":
                    produit_id = int(input("produit_id : ").strip())
                    promotion_percent = int(input("promotion_percent : ").strip())
                    region_id_promo = (input("region_id list (1 2 3 4) : ").split())
                    region_id = [int(i) for i in region_id_promo]
                    create_promotion(session, produit_id, promotion_percent, region_id)
                    add_log(session, "create", "Promotion")

                # --- Autres ---
                case _:
                    print("Erreur de saisie.")
                    input("Appuyez sur Entrée pour continuer...")
                    continue

            input("Opération terminée. Appuyez sur Entrée pour revenir au menu...")

    except Exception as e:
        print(f"Erreur : {e}")

# R - READ

def read_menu(session):
    try:
        while True:
            clear_output(wait=True)
            print("\n--- READ Menu ---")
            print("Fonctions possibles :")
            print("  a : read_promo")
            print("  b : read_produit")
            print("  c : read_command")
            print("  d : read_client")
            print("  q : quitter")

            action = input("Choisissez une action (a/b/c/d/q) : ").strip().lower()
            clear_output(wait=True)

            if action == "q":
                break

            # --- Limit ---
            limit_str = input("Limit (laisser vide pour aucun) : ").strip()
            limit = int(limit_str) if limit_str else None

            # --- Filter (placeholder simple) ---
            # Здесь можно вводить SQLAlchemy-выражения, но для простоты используем None
            filter = input("Filter expression (laisser vide pour aucun) : ").strip()
            filter_exp = eval(filter) if filter else None

            match action:
                case "a":
                    res = read_promo(session, limit=limit, filter_exp=filter_exp)
                    print(res[0], end="\n")
                    print(res[1])
                case "b":
                    res = read_produit(session, limit=limit, filter_exp=filter_exp)
                    print(res)
                case "c":
                    res = read_command(session, limit=limit, filter_exp=filter_exp)
                    print(res)
                case "d":
                    res = read_client(session, limit=limit, filter_exp=filter_exp)
                    print(res)
                case _:
                    print("Erreur de saisie.")
                    continue

            input("\nAppuyez sur Entrée pour continuer...")

    except Exception as e:
        print(f"Erreur : {e}")

def delete_menu(session):
    from IPython.display import clear_output  # если используешь Jupyter

    try:
        while True:
            tables = {
                "Commande": Commande,
                "Client": Client,
                "Promotion": Promotion,
                "DonnePersonnel": DonnePersonnel,
                "Produit": Produit
            } 
            clear_output(wait=True)
            print("\n---DELETE Menu ---")
            print("Fonctions possibles :")
            print("  a : delete_objet")
            print("  b : delete_filtre")
            print("  q : quitter")
            
            action = input("Choisissez une action (a/b/q) : ").strip().lower()
            clear_output(wait=True)

            if action == "q":
                break

            match action:
                case "a":
                    table_nom = input("Nom de la table : ").strip()
                    table_class = tables.get(table_nom)
                    obj_id = int(input("ID de l'objet à supprimer : ").strip())
                    delete_objet(session, table_class, obj_id)
                    add_log(session, "delete", table_nom, details=f"obj_id: {obj_id}")
                case "b":
                    table_nom = input("Nom de la table : ").strip()
                    table_class = tables.get(table_nom)
                    filter_exp = eval(input("Filtre SQLAlchemy (ex: Table.col == valeur) : ").strip())

                    delete_filtre(session, table_class, filter_exp)
                    add_log(session, "delete", table_nom, details=f"condution: {filter_exp}")
                case _:
                    print("Erreur de saisie.")
                    continue
    except Exception as e:
        print(f"Erreur : {e}")


def main():
    db_path = os.path.join(os.path.dirname(__file__), "BD_Ventes_de_jeux_video.db")
    engine = create_engine(f"sqlite:///{db_path}")

    # Création de la session
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        menu_admin(session)  # on passe la session à l'admin menu
    finally:
        session.close()  # fermeture propre de la session

if __name__ == "__main__":
    main()