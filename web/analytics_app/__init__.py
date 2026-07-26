"""NEWS ANALYTICS — раздел сводки новостей по компаниям, монтируется как отдельное Dash под-приложение.

Перенесено из отдельного проекта news-analytics (github.com/phumigator/...).
Оформление и навбар приведены к общему pipboy-стилю ZCYC (см. web/nav.py и
body.dash-pipboy в web/static/style.css) — обе Dash-подприложения используют
один и тот же тулбар/тему, а не расходящиеся копии.
"""
import dash
import dash_bootstrap_components as dbc

from .callbacks import register_callbacks
from .layout import create_layout
from dash_app.i18n import current_lang
from nav import build_nav_html


def create_analytics_app(server, url_base_pathname="/analytics/"):
    app = dash.Dash(
        __name__,
        server=server,
        url_base_pathname=url_base_pathname,
        external_stylesheets=[dbc.themes.BOOTSTRAP],
        title="News Analytics",
        suppress_callback_exceptions=True,
    )

    def interpolate_index(metas="", title="", css="", config="", scripts="",
                           app_entry="", favicon="", renderer=""):
        # Тот же паттерн, что в dash_app/__init__.py: вызывается на каждый
        # запрос, поэтому html[lang] и навбар строятся динамически по cookie 'lang'.
        return f"""<!DOCTYPE html>
<html lang="{current_lang()}">
<head>
    {metas}
    <title>{title}</title>
    {favicon}
    {css}
    <link rel="stylesheet" href="/static/style.css">
</head>
<body class="pipboy-page dash-pipboy analytics-page">
    {build_nav_html("/analytics/")}
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
        # Callable layout (не голый объект) — Dash зовёт это заново при каждом
        # `/_dash-layout`, внутри Flask request context, так перевод следует за cookie 'lang'.
        return create_layout()

    app.layout = serve_layout

    register_callbacks(app)
    return app
