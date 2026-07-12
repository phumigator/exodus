"""
ZCYC Dash-приложение, монтируемое как под-приложение Flask.
"""
import dash
import dash_bootstrap_components as dbc

from .layout import create_layout
from .callbacks_curve import register_callbacks as register_curve
from .callbacks_points import register_callbacks as register_points
from .callbacks_bonds import register_callbacks as register_bonds
from .callbacks_utils import register_callbacks as register_utils


NAV_HTML = """
<nav class="pipboy-nav">
    <a class="brand" href="/">EXODUS</a>
    <ul>
        <li><a href="/">Главная</a></li>
        <li><a href="/zcyc/" class="active">ZCYC</a></li>
        <li><a href="/transcription">Транскрибация</a></li>
        <li><a href="/about">Разработчик</a></li>
        <li><a class="disabled" href="#" tabindex="-1">Аналитика</a></li>
    </ul>
</nav>
"""


def create_dash_app(server, url_base_pathname="/zcyc/"):
    """Создаёт Dash-приложение, использующее переданный Flask-сервер."""
    app = dash.Dash(
        __name__,
        server=server,
        url_base_pathname=url_base_pathname,
        external_stylesheets=[dbc.themes.BOOTSTRAP],
        title="ZCYC",
        suppress_callback_exceptions=True,
    )

    # Тот же постоянный навбар, что и на Flask-страницах (web/templates/_nav.html),
    # но захардкожен, т.к. index_string — обычная Python-строка без Jinja.
    app.index_string = f"""<!DOCTYPE html>
<html>
<head>
    {{%metas%}}
    <title>{{%title%}}</title>
    {{%favicon%}}
    {{%css%}}
    <link rel="stylesheet" href="/static/style.css">
</head>
<body>
    {NAV_HTML}
    {{%app_entry%}}
    <footer>
        {{%config%}}
        {{%scripts%}}
        {{%renderer%}}
    </footer>
</body>
</html>
"""

    app.layout = create_layout()

    register_curve(app)
    register_points(app)
    register_bonds(app)
    register_utils(app)

    return app
