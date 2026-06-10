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

## Деплой на хостинге

1. Запустить web-сервис (Flask + Dash) на порту 8888, например через gunicorn:
   ```
   cd web && gunicorn -w 2 -b 127.0.0.1:8888 app:app
   ```
2. Запустить api-сервис (FastAPI) на порту 8000, с `--root-path /api`,
   чтобы внутренние ссылки и openapi-схема учитывали префикс `/api`,
   под которым сервис доступен через nginx:
   ```
   cd api && uvicorn main:app --host 127.0.0.1 --port 8000 --root-path /api
   ```
3. Установить `nginx/exodus.conf` в `/etc/nginx/sites-available/`,
   создать симлинк в `sites-enabled/`, заменить `server_name` на свой домен
   и перезагрузить nginx (`nginx -t && systemctl reload nginx`).
