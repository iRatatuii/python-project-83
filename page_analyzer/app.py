import os
from datetime import datetime
from urllib.parse import urlparse

import psycopg2
import validators
from dotenv import load_dotenv
from flask import Flask, abort, flash, redirect, render_template, request, url_for

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    print("DATABASE_URL не установлена")

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")


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

init_database()


@app.route("/")
def home():
    return render_template("index.html")


@app.get("/urls")
def urls_get():
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM urls ORDER BY id DESC")
                urls = cur.fetchall()
                print(urls)
                return render_template("urls.html", urls=urls)
    except psycopg2.Error as e:
        flash(f"Ошибка базы данных: {e}", "danger")
        return render_template("urls.html", urls=[])

@app.get("/urls/<id>")
def show_url(id):
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM urls WHERE id=%s", (id,))
                url = cur.fetchone()

                if url is None:
                    abort(404)

                return render_template("url.html", id=url[0], name=url[1], date=url[2])
    except psycopg2.Error as e:
        flash(f"Ошибка базы данных: {e}", "danger")
        abort(500)


@app.post("/urls")
def urls_post():
    data = request.form.get("url", "").strip()
    if not data:
        flash("URL не может быть пустым", "danger")
        return render_template("index.html")

    normalize_url = urlparse(data)
    url = f"{normalize_url.scheme}://{normalize_url.hostname}"

    if len(url) > 255:
        flash("URL не может быть длиннее 255 символов", "danger")
        return render_template("index.html")

    if not validators.url(url):
        flash("Некорректный URL", "danger")
        return render_template("index.html")

    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT id from urls WHERE name = %s", (url,))
                existing_url = cur.fetchone()

                if existing_url:
                    flash("Страница уже существует", "info")
                    return redirect(url_for("show_url", id=existing_url[0]))

                cur.execute(
                    "INSERT INTO urls (name, created_at) VALUES (%s, %s) RETURNING id",
                    (url, datetime.now()),
                )
                new_id = cur.fetchone()[0]
                conn.commit()

                flash("Страница успешно добавлена", "success")
                return redirect(url_for("show_url", id=new_id))

    except psycopg2.IntegrityError:
        flash("Такой URL уже существует", "info")
        return redirect(url_for("urls_get"))

    except psycopg2.Error as e:
        flash(f"Ошибка базы данных: {e}", "danger")
        return render_template("index.html")


@app.post("/urls/<id>/checks")
def check_url(id):
    flash("Проверка URL еще не реализована", "warning")
    return redirect(url_for("show_url", id=id))

@app.errorhandler(404)
def not_found(error):
    return render_template("404.html"), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template("500.html"), 500


if __name__ == "__main__":
    app.run(debug=os.getenv("FLASK_ENV") == "development")
