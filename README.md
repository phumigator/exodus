# Exodus

Фронтенд-платформа, объединяющая несколько служб:

1. **Dash-дашборд (ZCYC)** — встроен во `web/dash_app`, монтируется в Flask-приложение `web/app.py`.
2. **Сервис транскрибации/суммаризации** — `api/routers/transcription.py`, проксирует запросы к Ollama/Whisper на удалённом сервере.
3. **Сервис аналитики из Postgres** — `api/routers/analytics.py`, обращается к БД на том же удалённом сервере.
4. **Раздел "О разработчике"** — статическая страница `web/templates/about.html`.

## Архитектура

```
                ┌────────────┐
                │   nginx    │  reverse proxy
                └─────┬──────┘
        ┌─────────────┼──────────────┐
        │                             │
 ┌──────▼───────┐             ┌───────▼──────┐
 │  web (Flask) │             │  api (FastAPI)│
 │  + Dash app  │             │  transcription│
 │  + about page│             │  + analytics  │
 └──────────────┘             └───────┬───────┘
                                       │ API
                               ┌───────▼───────┐
                               │ Удалённый ПК  │
                               │ Ollama, Whisper│
                               │ Postgres       │
                               └───────────────┘
```

## Структура проекта

```
exodus/
├── web/            # Flask + Dash + статические страницы
│   ├── app.py
│   ├── dash_app/   # ZCYC dashboard (бывш. PythonProject_PET_ON_WEB)
│   ├── templates/
│   └── static/
├── api/            # FastAPI: транскрибация и аналитика
│   ├── main.py
│   └── routers/
│       ├── transcription.py
│       └── analytics.py
└── nginx/          # конфиг реверс-прокси для хостинга
```
