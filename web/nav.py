"""
Общий HTML-тулбар (навбар) для всех Dash-подприложений (ZCYC, News Analytics).

Та же разметка, что и у Flask-страниц (web/templates/_nav.html), но построена
на лету, т.к. Dash не использует Jinja — единая функция, чтобы навбар не
расходился между подприложениями при будущих правках.
"""
from dash_app.i18n import current_lang, t

NAV_LINKS = [
    ("/", "nav_home"),
    ("/zcyc/", "nav_zcyc"),
    ("/transcription", "nav_transcription"),
    ("/analytics/", "nav_analytics"),
    ("/about", "nav_about"),
]


def build_nav_html(active_href: str) -> str:
    lang = current_lang()
    items = []
    for href, label_key in NAV_LINKS:
        active_cls = ' class="active"' if href == active_href else ''
        items.append(f'<li><a href="{href}"{active_cls}>{t(label_key)}</a></li>')
    links_html = "\n        ".join(items)
    ru_cls = ' class="active"' if lang == 'ru' else ''
    en_cls = ' class="active"' if lang == 'en' else ''

    return f"""<nav class="pipboy-nav">
    <a class="brand" href="/">PHUMIGATOR EXODUS</a>
    <ul>
        {links_html}
    </ul>
    <div class="lang-switch">
        <a href="/set-language?lang=ru&next={active_href}"{ru_cls}>RU</a>
        <a href="/set-language?lang=en&next={active_href}"{en_cls}>EN</a>
    </div>
</nav>"""
