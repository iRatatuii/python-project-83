import psycopg2
from flask import (
    Flask,
    abort,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)

from .config import FLASK_ENV, SECRET_KEY
from .database import (
    add_url,
    add_url_check,
    get_all_urls,
    get_url,
    get_url_checks,
    get_url_id_by_name,
    init_database,
)
from .url_normalizer import analyze_url, prepare_url

app = Flask(__name__)
app.config["SECRET_KEY"] = SECRET_KEY  # NOSONAR

if not app.config["SECRET_KEY"]:  # NOSONAR
    raise RuntimeError("SECRET_KEY не установлен")


@app.route("/")
def home():
    return render_template("index.html")


@app.get("/urls")
def urls_get():
    try:
        urls = get_all_urls()
        return render_template("urls.html", urls=urls)
    except psycopg2.Error as e:
        flash(f"Ошибка базы данных: {e}", "danger")
        return render_template("urls.html", urls=[])


@app.get("/urls/<int:id>")
def show_url(id):
    try:
        url = get_url(id)
        checks = get_url_checks(id)
        return render_template("url.html", url=url, checks=checks)
    except psycopg2.Error as e:
        flash(f"Ошибка базы данных: {e}", "danger")
        abort(500)


@app.post("/urls")
def urls_post():
    data = request.form.get("url", "")

    url, error = prepare_url(data)

    if error:
        flash(error, "danger")
        return render_template("index.html"), 422

    try:
        existing_url = get_url_id_by_name(url)

        if existing_url:
            flash("Страница уже существует", "info")
            return redirect(url_for("show_url", id=existing_url[0]))

        new_id = add_url(url)
        flash("Страница успешно добавлена", "success")
        return redirect(url_for("show_url", id=new_id))

    except psycopg2.IntegrityError:
        flash("Такой URL уже существует", "info")
        return redirect(url_for("urls_get"))

    except psycopg2.Error as e:
        flash(f"Ошибка базы данных: {e}", "danger")
        return render_template("index.html")


@app.post("/urls/<int:id>/checks")
def check_url(id):
    try:

        url = get_url(id)

        if url is None:
            abort(404)
        data = analyze_url(url["name"])

        if data is None:
            flash("Произошла ошибка при проверке", "danger")
            return redirect(url_for("show_url", id=id))

        add_url_check(id, data)

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
    app.run(debug=FLASK_ENV == "development")
