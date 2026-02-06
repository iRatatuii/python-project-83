import psycopg2

from .config import DATABASE_URL


def get_db_connection():
    return psycopg2.connect(DATABASE_URL)


def init_database():
    try:
        with open("database.sql") as f:
            sql_commands = f.read()
        with get_db_connection() as conn:

            conn.autocommit = True
            with conn.cursor() as cur:
                cur.execute(sql_commands)
                print("База данных успешно инициализирована")

    except FileNotFoundError:
        print("Файл database.sql не найден, пропускаем инициализацию")

    except psycopg2.Error as e:
        print(f"Ошибка подключения к базе данных: {e}")
