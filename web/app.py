"""
Главное Flask-приложение Exodus: монтирует Dash-дашборд и отдаёт статические разделы.
"""
from flask import Flask, render_template

from dash_app import create_dash_app


def create_app():
    server = Flask(__name__)

    create_dash_app(server, url_base_pathname="/zcyc/")

    @server.route("/")
    def index():
        return render_template("index.html")

    @server.route("/about")
    def about():
        return render_template("about.html")

    return server


app = create_app()

if __name__ == "__main__":
    print("Запуск Exodus...")
    print("Главная страница: http://localhost:8888/")
    print("ZCYC Dashboard:    http://localhost:8888/zcyc/")
    app.run(debug=True, host="0.0.0.0", port=8888)
