"""Цветовая схема дашборда — по методике skill'а dataviz (references/palette.md).
Пока только light-режим: тёмная тема добавится при переносе раздела в EXODUS.
"""

SURFACE = "#fcfcfb"
PAGE = "#f9f9f7"
TEXT_PRIMARY = "#0b0b0b"
TEXT_SECONDARY = "#52514e"
TEXT_MUTED = "#898781"
GRIDLINE = "#e1e0d9"
BASELINE = "#c3c2b7"

# Категориальный слот 1 (sequential magnitude: "новостей по компании")
SEQUENTIAL_BLUE = "#2a78d6"

# Diverging pair для sentiment (Likert-подобная шкала: negative <-> positive)
SENTIMENT_COLORS = {
    "positive": "#2a78d6",   # diverging blue
    "negative": "#e34948",   # diverging red (series slot 8)
    "neutral": "#898781",    # muted ink — видимый нейтральный сегмент
}

SENTIMENT_ORDER = ["negative", "neutral", "positive"]

SENTIMENT_LABELS_RU = {
    "positive": "Позитив",
    "negative": "Негатив",
    "neutral": "Нейтрально",
}

FONT_FAMILY = 'system-ui, -apple-system, "Segoe UI", sans-serif'
