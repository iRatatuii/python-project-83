import os
from datetime import datetime

import psycopg2
import validators
from dotenv import load_dotenv
from flask import Flask, abort, flash, redirect, render_template, request, url_for

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    print("DATABASE_URL не установлена")
    exit(1)

try:
    with open("database.sql") as f:
        sql_commands = f.read()

    conn = psycopg2.connect(DATABASE_URL)
    conn.autocommit = True
    cur = conn.cursor()
    cur.execute(sql_commands)
    print("База данных успешно инициализирована")

    cur.execute("SELECT * FROM urls")


except psycopg2.Error as e:
    print(f"Ошибка подключения к базе данных: {e}")


app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")


@app.route("/")
def home():
    return render_template("index.html")


@app.get("/urls")
def urls_get():
    cur.execute("SELECT * FROM urls ORDER BY id DESC")
    urls = cur.fetchall()
    print(urls)
    return render_template("urls.html", urls=urls)


@app.get("/urls/<id>")
def show_url(id):
    cur.execute("SELECT * FROM urls WHERE id=%s", (id,))
    url = cur.fetchone()
    if url is None:
        abort(404)
    print(url)
    return render_template("url.html", id=url[0], name=url[1], date=url[2])


@app.post("/urls")
def urls_post():
    data = request.form.get("url", "").strip()
    
    if len(data) > 255:
        flash("URL не может быть длиннее 255 символов", "danger")
        return render_template("index.html")

    if not data:
        flash("URL не может быть пустым", "danger")

    if not validators.url(data):
        flash("Некорректный URL", "danger")
        return render_template("index.html")
    print(data)

    try:
        cur.execute("""SELECT id from urls WHERE name = %s""", (data,))
        existing_url = cur.fetchone()
        if existing_url:
            flash("Страница уже существует", "info")
            return redirect(url_for("show_url", id=existing_url[0]))

        cur.execute(
            """INSERT INTO urls (name, created_at) VALUES (%s, %s) RETURNING id""",
            (data, datetime.today()),
        )
        new_id = cur.fetchone()[0]
        conn.commit()

        flash("Страница успешно добавлена", "success")
        return redirect(url_for("show_url", id=new_id))

    except psycopg2.Error as e:
        print(f"Ошибка подключения к базе данных: {e}")


@app.post("/urls/<id>/checks")
def check_url(id):
    pass


if __name__ == "__main__":
    app.run(debug=True)
