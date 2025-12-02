
import logging

from components import BD_Ventes_de_jeux_video, engine, SessionLocal
from components.models import *           # или точечные импорты
from components.crud import *             # или точечные импорты

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    )

def menu_admin():
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
                    creation_menu()
                case "r":
                    read_menu()
                case "u":
                    update_table(table_nom, data_id, **kwargs)
                case "d":
                    delete_menu()
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

def creation_menu():
    try:
        while True:
            clear_output(wait=True)
            print("\n---CREATION Menu ---")
            print("Fonctions possibles :")
            print("  a : create_donne_personnel")
            print("  b : create_client")
            print("  c : create_commande")
            print("  d : create_promotion")
       
            action = input("Choisissez une action (a/b/c/d) : ").strip().lower()
            clear_output(wait=True)
            match action:
                case "a":
                    create_donne_personnel(session: Session, login, mot_de_passe_hash)
                case "r":
                    create_client(session: Session, age_id:int, region_id:int)
                case "u":
                    create_commande(session: Session, client_id, produit_id, nb_produit)
                case "d":
                    create_promotion(session: Session, produit_id:int, promotion_percent:int, region_id_promo:int)
                case _:
                    print("Erreur de saisie.")
                    continue
    except Exception as e:
        print(f"Erreur : {e}")

def delete_menu():
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
                    delete_objet(session: Session, table_nom, id)
                case "b":
                    delete_filtre(session: Session, filter_exp)
                case _:
                    print("Erreur de saisie.")
                    continue
    except Exception as e:
        print(f"Erreur : {e}")

def main():

    setup_logging()
    logger = logging.getLogger(__name__)
    logger.info("Initializing DB")

    # Инициализация БД
    init_db()

    # Создаем сессию
    session = SessionLocal()
    logger.info("Session started")
    # Пример вызовов CRUD
    menu_admin()

    session.close()
    logger.info("Session closed")

if __name__ == "__main__":
    main()