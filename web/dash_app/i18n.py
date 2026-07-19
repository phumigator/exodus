"""
Языковой хелпер для Dash-приложения ZCYC.

В отличие от Flask-страниц (где язык берётся из `g.lang` в `before_request`),
Dash-колбэки и построение layout выполняются вне Jinja, но всё ещё внутри
Flask request context (и первая отдача index-страницы, и AJAX-запросы
`_dash-layout`/`_dash-update-component` — обычные Flask-роуты) — поэтому язык
читается прямо из cookie через `flask.request` при каждом обращении.
"""
from flask import request

from translations import DEFAULT_LANG, SUPPORTED_LANGS, translate

LANG_COOKIE = "lang"


def current_lang() -> str:
    lang = request.cookies.get(LANG_COOKIE, DEFAULT_LANG)
    return lang if lang in SUPPORTED_LANGS else DEFAULT_LANG


def t(key: str) -> str:
    return translate(current_lang(), key)


# Цвета Pip-Boy темы для мест, где CSS не достаёт (inline-стили dash_table,
# цвета фона/сетки графика Plotly) — синхронизированы с переменными
# --pip-panel/--pip-green-dim/--pip-green/--pip-text в web/static/style.css.
PIPBOY_COLORS = {
    "ru": {"panel": "#0d1912", "dim": "#1f7a3d", "green": "#39ff6a", "text": "#7fe89c"},
    "en": {"panel": "#191208", "dim": "#8a5a12", "green": "#ffb000", "text": "#e8b96a"},
}


def pip_colors() -> dict:
    return PIPBOY_COLORS.get(current_lang(), PIPBOY_COLORS["ru"])
