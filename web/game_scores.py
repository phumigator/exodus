"""
Общие таблицы рекордов браузерных игр: SQLite-файл и JSON API для самих игр.

Файл лежит в EXODUS_GAMES_DB (по умолчанию web/games_data/scores.sqlite) и не хранится в git,
поэтому обновление сайта его не затирает. Игра присылает результат сама, так что
подделать его можно; лимиты ниже лишь не дают засорить таблицу и базу.
"""
import os
import sqlite3
from pathlib import Path

from flask import jsonify, request

DB_PATH = Path(os.environ.get(
    "EXODUS_GAMES_DB",
    Path(__file__).resolve().parent / "games_data" / "scores.sqlite",
))

TOP_SIZE = 10
KEEP_ROWS = 100  # на игру: всё, что ниже, удаляется при записи
MAX_NAME_LENGTH = 16
MAX_SCORE = 1_000_000


def _connect():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DB_PATH, timeout=5)
    connection.execute(
        "CREATE TABLE IF NOT EXISTS scores ("
        " id INTEGER PRIMARY KEY AUTOINCREMENT,"
        " game TEXT NOT NULL,"
        " name TEXT NOT NULL,"
        " coins INTEGER NOT NULL)"
    )
    return connection


def top_scores(game: str):
    """Лучшие результаты; при равенстве выше тот, кто внёс раньше."""
    with _connect() as connection:
        rows = connection.execute(
            "SELECT name, coins FROM scores WHERE game = ? ORDER BY coins DESC, id ASC LIMIT ?",
            (game, TOP_SIZE),
        ).fetchall()
    return [{"name": name, "coins": coins} for name, coins in rows]


def add_score(game: str, name: str, coins: int):
    with _connect() as connection:
        connection.execute("INSERT INTO scores (game, name, coins) VALUES (?, ?, ?)", (game, name, coins))
        connection.execute(
            "DELETE FROM scores WHERE game = ? AND id NOT IN ("
            " SELECT id FROM scores WHERE game = ? ORDER BY coins DESC, id ASC LIMIT ?)",
            (game, game, KEEP_ROWS),
        )


def _clean_name(raw):
    if not isinstance(raw, str):
        return None
    name = "".join(ch for ch in raw if ch.isprintable()).strip()[:MAX_NAME_LENGTH]
    return name or None


def handle_scores(game: str):
    """GET — таблица; POST {"name", "coins"} — добавить результат и вернуть таблицу."""
    if request.method == "POST":
        payload = request.get_json(silent=True)
        if not isinstance(payload, dict):
            return jsonify(error="bad json"), 400
        name = _clean_name(payload.get("name"))
        coins = payload.get("coins")
        if name is None or isinstance(coins, bool) or not isinstance(coins, int) or not 1 <= coins <= MAX_SCORE:
            return jsonify(error="bad score"), 400
        add_score(game, name, coins)
    return jsonify(entries=top_scores(game))
