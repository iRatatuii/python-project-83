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


def get_all_urls():
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                        SELECT 
                        urls.id, 
                        urls.name,
                        urls.created_at,
                        MAX(url_checks.created_at) as last_check_date,
                        (
                            SELECT status_code 
                            FROM url_checks
                            WHERE url_id = urls.id
                            ORDER BY id DESC
                            LIMIT 1
                        ) as last_status_code
                        FROM urls 
                        LEFT JOIN url_checks 
                        ON urls.id = url_checks.url_id
                        GROUP BY urls.id, urls.name, urls.created_at
                        ORDER BY urls.id DESC
                    """
            )
            urls_all = cur.fetchall()
            urls = [
                {
                    "id": row[0],
                    "name": row[1],
                    "created_at": row[2],
                    "last_check_date": row[3],
                    "last_check_status": row[4],
                }
                for row in urls_all
            ]
            return urls


def get_url(url_id):
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM urls WHERE id=%s", (url_id,))
            url = cur.fetchone()
            if url is None:
                return None
            
            url = {"id": url[0], "name": url[1], "created_at": url[2]}
            return url


def get_url_checks(url_id):
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                    SELECT 
                    id,
                    status_code,
                    h1,
                    title,
                    description,
                    created_at 
                    FROM url_checks 
                    WHERE url_id = %s 
                    ORDER BY id DESC
                """,
                (url_id,),
            )

            checks = [
                {
                    "id": row[0],
                    "status_code": row[1],
                    "h1": row[2],
                    "title": row[3],
                    "description": row[4],
                    "created_at": row[5],
                }
                for row in cur.fetchall()
            ]
            return checks


def get_url_id_by_name(name):
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id from urls WHERE name = %s", (name,))
            existing_url = cur.fetchone()
            return existing_url


def add_url(name):
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                    "INSERT INTO urls (name) VALUES (%s) RETURNING id", (name,),
                )
            row = cur.fetchone()
            return row[0] if row else None
        conn.commit()


def add_url_check(id, data):
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                    INSERT INTO url_checks 
                    (url_id, status_code, h1, title, description)
                    VALUES (%s, %s, %s, %s, %s)
                    """,
                (
                    id,
                    data["status_code"],
                    data["h1"],
                    data["title"],
                    data["description"],
                ),
            )
        conn.commit()
