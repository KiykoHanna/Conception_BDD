# import

from IPython.display import clear_output
import json

from sqlalchemy import  create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import func
from components.models import *           # или точечные импорты
from components.crud import *             # или точечные импорты


def menu_admin(session):
    """
    La fonction affiche un menu interactif destiné à l’administrateur.
    Elle permet d’exécuter différentes opérations sur les utilisateurs : création, lecture, mise à jour, suppression.
    La fonction utilise match/case pour gérer les choix de manière claire et structurée. 
    Elle inclut également une gestion d’erreurs afin d’éviter l’arrêt du programme en cas de saisie incorrecte ou d’exception.
    """
    try:
        while True:
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
                    table_nom = str(input("Table: "))
                    data_id = int(input("ID: "))
                    raw_kwargs = input("kwargs (en JSON, ex: {\"name\": \"Alice\"}): ")

                    kwargs = json.loads(raw_kwargs) if raw_kwargs else {}

                    update_table(session, table_nom, data_id, **kwargs)
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
            print("  a : create_donne_personnel")
            print("  b : create_client")
            print("  c : create_commande")
            print("  d : create_promotion")

            action = input("Choisissez une action (a/b/c/d) : ").strip().lower()
            clear_output(wait=True)

            match action:

                # --- A ---
                case "a":
                    login = input("login : ").strip()
                    mot_de_passe = input("mot_de_passe : ").strip()
                    mot_de_passe_hash = hash(mot_de_passe)
                    create_donne_personnel(session, login, mot_de_passe_hash)

                # --- B ---
                case "b":
                    age_id = int(input("age_id (0–3) : ").strip())
                    region_id = int(input("region_id (0–3) : ").strip())
                    create_client(session, age_id, region_id)

                # --- C ---
                case "c":
                    client_id = int(input("client_id : ").strip())
                    produit_id = int(input("produit_id : ").strip())
                    nb_produit = int(input("nb_produit : ").strip())
                    create_commande(session, client_id, produit_id, nb_produit)

                # --- D ---
                case "d":
                    produit_id = int(input("produit_id : ").strip())
                    promotion_percent = int(input("promotion_percent : ").strip())
                    region_id_promo = int(input("region_id_promo : ").strip())
                    create_promotion(session, produit_id, promotion_percent, region_id_promo)

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
            filter_exp = (filter) if filter else None

            match action:
                case "a":
                    res = read_promo(session, limit=limit, filter_exp=filter_exp)
                    print(res)
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
            clear_output(wait=True)
            print("\n---DELETE Menu ---")
            print("Fonctions possibles :")
            print("  a : delete_objet")
            print("  b : delete_filtre")
            
            action = input("Choisissez une action (a/b) : ").strip().lower()
            clear_output(wait=True)

            match action:
                case "a":
                    table_nom = input("Nom de la table : ").strip()
                    obj_id = input("ID de l'objet à supprimer : ").strip()
                    delete_objet(session, table_nom, obj_id)
                case "b":
                    table_nom = input("Nom de la table : ").strip()
                    filter_exp = input("Filtre SQLAlchemy (ex: Table.col == valeur) : ").strip()

                    delete_filtre(session, table_nom, filter_exp)
                case _:
                    print("Erreur de saisie.")
                    continue
    except Exception as e:
        print(f"Erreur : {e}")


def main():
    # Création de l'engine
    engine = create_engine("sqlite:///BD_Ventes_de_jeux_video.db") 

    # Création de la session
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        menu_admin(session)  # on passe la session à l'admin menu
    finally:
        session.close()  # fermeture propre de la session

if __name__ == "__main__":
    main()