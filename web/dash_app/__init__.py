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
from .i18n import current_lang
from nav import build_nav_html


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

    def interpolate_index(metas="", title="", css="", config="", scripts="",
                           app_entry="", favicon="", renderer=""):
        # Вызывается на каждый запрос страницы (Dash.index — обычный Flask-роут),
        # поэтому html[lang] (для янтарной темы из style.css) и навбар можно
        # строить динамически по cookie 'lang', как и на Flask-страницах.
        return f"""<!DOCTYPE html>
<html lang="{current_lang()}">
<head>
    {metas}
    <title>{title}</title>
    {favicon}
    {css}
    <link rel="stylesheet" href="/static/style.css">
</head>
<body class="pipboy-page dash-pipboy zcyc-page">
    {build_nav_html("/zcyc/")}
    {app_entry}
    <footer>
        {config}
        {scripts}
        {renderer}
    </footer>
</body>
</html>
"""

    app.interpolate_index = interpolate_index

    def serve_layout():
        # Callable layout: Dash re-invokes это при каждой отдаче `/_dash-layout`,
        # тоже внутри Flask request context, так что перевод следует за cookie 'lang'.
        return create_layout()

    app.layout = serve_layout

    register_curve(app)
    register_points(app)
    register_bonds(app)
    register_utils(app)

    return app
