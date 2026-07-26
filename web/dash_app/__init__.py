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
from .i18n import current_lang, t


def _build_nav_html():
    """Тот же постоянный навбар, что и на Flask-страницах (web/templates/_nav.html),
    но захардкожен и построен на лету, т.к. Dash не использует Jinja — язык и
    активная ссылка переключателя языка берутся из cookie на каждый запрос."""
    lang = current_lang()
    nav_links = [
        ("/", t('nav_home')),
        ("/zcyc/", t('nav_zcyc')),
        ("/transcription", t('nav_transcription')),
        ("/analytics/", t('nav_analytics')),
        ("/about", t('nav_about')),
    ]
    items = []
    for href, label in nav_links:
        active_cls = ' class="active"' if href == "/zcyc/" else ''
        items.append(f'<li><a href="{href}"{active_cls}>{label}</a></li>')
    links_html = "\n        ".join(items)
    ru_cls = ' class="active"' if lang == 'ru' else ''
    en_cls = ' class="active"' if lang == 'en' else ''

    return f"""<nav class="pipboy-nav">
    <a class="brand" href="/">PHUMIGATOR EXODUS</a>
    <ul>
        {links_html}
    </ul>
    <div class="lang-switch">
        <a href="/set-language?lang=ru&next=/zcyc/"{ru_cls}>RU</a>
        <a href="/set-language?lang=en&next=/zcyc/"{en_cls}>EN</a>
    </div>
</nav>"""


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
<body class="pipboy-page zcyc-page">
    {_build_nav_html()}
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
