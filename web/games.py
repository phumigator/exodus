"""
Браузерные игры (Unity WebGL): реестр игр и поиск файлов сборки.

Каждая сборка лежит в EXODUS_GAMES_DIR/<slug>/ (по умолчанию web/games_builds/)
ровно в том виде, в каком её выдаёт Unity (Build/, TemplateData/, index.html),
и раздаётся Flask под /games-build/<slug>/ с нужными Content-Encoding и MIME.
"""
import os
from pathlib import Path

from flask import abort, send_from_directory

GAMES_DIR = Path(os.environ.get(
    "EXODUS_GAMES_DIR",
    Path(__file__).resolve().parent / "games_builds",
))

# slug -> ключи перевода (заголовок и описание карточки)
GAMES = {
    "seaplane": ("game_seaplane_title", "game_seaplane_desc"),
}

# Сжатые файлы Unity: расширение -> Content-Encoding
_ENCODINGS = {".br": "br", ".gz": "gzip"}

# MIME по "внутреннему" расширению (после снятия .br/.gz)
_MIME_TYPES = {
    ".js": "application/javascript",
    ".wasm": "application/wasm",
    ".data": "application/octet-stream",
    ".json": "application/json",
    ".unityweb": "application/octet-stream",
}


def _pick(build_dir: Path, base: str, suffix: str):
    """Ищет файл base+suffix с любым сжатием (без, .br, .gz, .unityweb)."""
    for ext in ("", ".br", ".gz", ".unityweb"):
        candidate = build_dir / f"{base}{suffix}{ext}"
        if candidate.is_file():
            return candidate.name
    return None


def find_unity_build(slug: str):
    """
    Возвращает имена файлов сборки для createUnityInstance или None,
    если сборки ещё нет (тогда страница показывает заглушку).
    """
    build_dir = GAMES_DIR / slug / "Build"
    loaders = sorted(build_dir.glob("*.loader.js")) if build_dir.is_dir() else []
    if not loaders:
        return None
    base = loaders[0].name[: -len(".loader.js")]
    files = {
        "loader": loaders[0].name,
        "data": _pick(build_dir, base, ".data"),
        "framework": _pick(build_dir, base, ".framework.js"),
        "code": _pick(build_dir, base, ".wasm"),
    }
    if not all(files.values()):
        return None
    files["url"] = f"/games-build/{slug}/Build"
    return files


def send_build_file(slug: str, filename: str):
    """Отдаёт файл сборки с Content-Encoding/MIME, которые ждёт загрузчик Unity."""
    game_dir = GAMES_DIR / slug
    if not game_dir.is_dir():
        abort(404)
    name, ext = os.path.splitext(filename)
    encoding = _ENCODINGS.get(ext)
    inner_ext = os.path.splitext(name)[1] if encoding else ext
    mimetype = _MIME_TYPES.get(inner_ext)
    response = send_from_directory(game_dir, filename, mimetype=mimetype)
    if encoding:
        response.headers["Content-Encoding"] = encoding
    return response
