
import logging

from components import BD_Ventes_de_jeux_video, engine, SessionLocal
from components.models import *           # или точечные импорты
from components.crud import *             # или точечные импорты

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    )

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
    # new_client = create_client(session, name="Alice", email="alice@mail.com")
    # client = get_client_by_id(session, 1)
    # products = list_products(session, limit=10)

    # ... ваша логика ...

    session.close()
    logger.info("Session closed")

if __name__ == "__main__":
    main()