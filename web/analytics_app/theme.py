"""Цветовая схема дашборда NEWS ANALYTICS.

Фон/текст/сетка берутся из общей Pip-Boy палитры (dash_app.i18n.pip_colors) —
та же тема, что и у ZCYC, переключается по языку (зелёная RU / янтарная EN),
а не задаётся отдельно. Здесь остаются только вещи, не зависящие от темы:
семантические цвета тональности (Likert-подобная шкала negative<->positive) и
исходная методика по skill'у dataviz (references/palette.md), от которой они
унаследованы.
"""

# Diverging pair для sentiment (Likert-подобная шкала: negative <-> positive) —
# фиксированные цвета, одинаковые в обеих темах, чтобы позитив/негатив
# оставались узнаваемыми независимо от зелёной/янтарной палитры фона.
SENTIMENT_COLORS = {
    "positive": "#2a78d6",
    "negative": "#e34948",
    "neutral": "#898781",
}

SENTIMENT_ORDER = ["negative", "neutral", "positive"]

# Категориальный слот 1 (sequential magnitude: "новостей по компании")
SEQUENTIAL_BLUE = "#2a78d6"
