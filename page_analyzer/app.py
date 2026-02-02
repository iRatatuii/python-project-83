import os
from urllib.parse import urlparse

import psycopg2
import requests
import validators
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from flask import Flask, abort, flash, redirect, render_template, request, url_for

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    print("DATABASE_URL не установлена")

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")

if not app.config["SECRET_KEY"]:
    raise RuntimeError("SECRET_KEY не установлен")


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


@app.route("/")
def home():
    return render_template("index.html")


@app.get("/urls")
def urls_get():
    try:
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
                urls = []
                for row in cur.fetchall():
                    urls.append(
                        {
                            "id": row[0],
                            "name": row[1],
                            "created_at": row[2],
                            "last_check_date": row[3],
                            "last_check_status": row[4],
                        }
                    )
                return render_template("urls.html", urls=urls)
    except psycopg2.Error as e:
        flash(f"Ошибка базы данных: {e}", "danger")
        return render_template("urls.html", urls=[])


@app.get("/urls/<int:id>")
def show_url(id):
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM urls WHERE id=%s", (id,))
                url = cur.fetchone()
                if url is None:
                    abort(404)
                url = {"id": url[0], "name": url[1], "created_at": url[2]}

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
                    (id,),
                )

                checks = []
                for row in cur.fetchall():
                    checks.append(
                        {
                            "id": row[0],
                            "status_code": row[1],
                            "h1": row[2],
                            "title": row[3],
                            "description": row[4],
                            "created_at": row[5],
                        }
                    )

                return render_template("url.html", url=url, checks=checks)
    except psycopg2.Error as e:
        flash(f"Ошибка базы данных: {e}", "danger")
        abort(500)


@app.post("/urls")
def urls_post():
    data = request.form.get("url", "").strip()
    if not data:
        flash("URL не может быть пустым", "danger")
        return render_template("index.html"), 422

    normalize_url = urlparse(data)
    url = f"{normalize_url.scheme}://{normalize_url.hostname}"

    if len(url) > 255:
        flash("URL не может быть длиннее 255 символов", "danger")
        return render_template("index.html"), 422

    if not validators.url(url):
        flash("Некорректный URL", "danger")
        return render_template("index.html"), 422
    
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT id from urls WHERE name = %s", (url,))
                existing_url = cur.fetchone()

                if existing_url:
                    flash("Страница уже существует", "info")
                    return redirect(url_for("show_url", id=existing_url[0]))

                cur.execute(
                    "INSERT INTO urls (name) VALUES (%s) RETURNING id",
                    (url,),
                )
                new_id = cur.fetchone()[0]

                flash("Страница успешно добавлена", "success")
                return redirect(url_for("show_url", id=new_id))

    except psycopg2.IntegrityError:
        flash("Такой URL уже существует", "info")
        return redirect(url_for("urls_get"))

    except psycopg2.Error as e:
        flash(f"Ошибка базы данных: {e}", "danger")
        return render_template("index.html")


def analyze_url(url):
    try:
        resp = requests.get(url, timeout=5)
        resp.raise_for_status()

        soup = BeautifulSoup(resp.text, "html.parser")

        h1 = soup.h1.string if soup.h1 else ""
        title = soup.title.string if soup.title else ""

        description_tag = soup.find("meta", attrs={"name": "description"})
        description = description_tag["content"] if description_tag else ""

        return {
            "status_code": resp.status_code,
            "h1": h1,
            "title": title,
            "description": description,
        }

    except requests.RequestException:
        return None


@app.post("/urls/<int:id>/checks")
def check_url(id):
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT name FROM urls WHERE id = %s", (id,))
                url = cur.fetchone()
                if url is None:
                    abort(404)

                data = analyze_url(url[0])

                if data is None:
                    flash("Произошла ошибка при проверке", "danger")
                    return redirect(url_for("show_url", id=id))

                cur.execute(
                    """
                    INSERT INTO url_checks (url_id, status_code, h1, title, description)
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

                flash("Страница успешно проверена", "success")
                return redirect(url_for("show_url", id=id))

    except psycopg2.Error as e:
        flash(f"Ошибка базы данных: {e}", "danger")
        abort(500)


@app.errorhandler(404)
def not_found(error):
    return render_template("404.html"), 404


@app.errorhandler(500)
def internal_error(error):
    return render_template("500.html"), 500


if __name__ == "__main__":
    init_database()
    app.run(debug=os.getenv("FLASK_ENV") == "development")
