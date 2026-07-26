"""
Главное Flask-приложение Phumigator Exodus: монтирует Dash-дашборд и отдаёт статические разделы.
"""
import os

from dotenv import load_dotenv

load_dotenv()

from flask import Flask, g, redirect, render_template, request

from analytics_app import create_analytics_app
from dash_app import create_dash_app
from translations import DEFAULT_LANG, SUPPORTED_LANGS, TRANSLATIONS, translate

# В проде nginx проксирует FastAPI под /api/ (см. nginx/exodus.conf);
# локально сервисы запущены раздельно, поэтому обращаемся к API напрямую.
API_BASE_URL = os.environ.get("EXODUS_API_BASE_URL", "http://localhost:8000")

LANG_COOKIE = "lang"
LANG_COOKIE_MAX_AGE = 60 * 60 * 24 * 365  # год


def create_app():
    server = Flask(__name__)

    create_dash_app(server, url_base_pathname="/zcyc/")
    create_analytics_app(server, url_base_pathname="/analytics/")

    @server.before_request
    def resolve_language():
        g.lang = request.cookies.get(LANG_COOKIE, DEFAULT_LANG)
        if g.lang not in SUPPORTED_LANGS:
            g.lang = DEFAULT_LANG

    server.jinja_env.globals["t"] = lambda key: translate(g.lang, key)

    @server.route("/set-language")
    def set_language():
        lang = request.args.get("lang", DEFAULT_LANG)
        if lang not in SUPPORTED_LANGS:
            lang = DEFAULT_LANG
        next_path = request.args.get("next", "/")
        if not next_path.startswith("/"):
            next_path = "/"
        response = redirect(next_path)
        response.set_cookie(LANG_COOKIE, lang, max_age=LANG_COOKIE_MAX_AGE)
        return response

    @server.route("/")
    def index():
        return render_template("index.html")

    @server.route("/about")
    def about():
        return render_template("about.html")

    @server.route("/transcription")
    def transcription():
        return render_template(
            "transcription.html",
            api_base_url=API_BASE_URL,
            i18n_json={key: translate(g.lang, key) for key in TRANSLATIONS[DEFAULT_LANG] if key.startswith("js_")},
        )

    return server


app = create_app()

if __name__ == "__main__":
    print("Запуск Phumigator Exodus...")
    print("Главная страница: http://localhost:8888/")
    print("ZCYC Dashboard:    http://localhost:8888/zcyc/")
    app.run(debug=True, host="0.0.0.0", port=8888)
