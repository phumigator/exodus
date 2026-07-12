# Phumigator Exodus

Фронтенд-платформа, объединяющая несколько служб:

1. **Dash-дашборд (ZCYC)** — встроен во `web/dash_app`, монтируется в Flask-приложение `web/app.py`.
2. **Сервис транскрибации/суммаризации** — `api/routers/transcription.py`, распознаёт речь через Whisper на удалённом сервере и суммаризирует текст через внешний LLM API [OpenRouter](https://openrouter.ai/).
3. **Сервис аналитики из Postgres** — `api/routers/analytics.py`, обращается к БД на том же удалённом сервере.
4. **Раздел "О разработчике"** — статическая страница `web/templates/about.html`.

## Архитектура

```
                ┌────────────┐
                │   nginx    │  reverse proxy
                └─────┬──────┘
        ┌─────────────┼──────────────┐
        │                             │
 ┌──────▼───────┐             ┌───────▼───────┐
 │  web (Flask) │             │  api (FastAPI) │
 │  + Dash app  │             │  transcription │
 │  + about page│             │  + analytics   │
 └──────────────┘             └───────┬────────┘
                                       │
                          ┌────────────┼─────────────┐
                          │            │             │
                   ┌──────▼─────┐ ┌────▼────┐ ┌──────▼──────┐
                   │ Удалённый  │ │OpenRouter│ │  Postgres   │
                   │ Whisper    │ │ (LLM API)│ │             │
                   └────────────┘ └─────────┘ └─────────────┘
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

1. Запустить web-сервис (Flask + Dash) на порту 8888, например через gunicorn.
   `EXODUS_API_BASE_URL` должен указывать на `/api` (относительный путь через nginx),
   иначе браузер будет пытаться обращаться к `http://localhost:8000` напрямую:
   ```
   cd web && EXODUS_API_BASE_URL=/api gunicorn -w 2 -b 127.0.0.1:8888 app:app
   ```
2. Запустить api-сервис (FastAPI) на порту 8000, с `--root-path /api`,
   чтобы внутренние ссылки и openapi-схема учитывали префикс `/api`,
   под которым сервис доступен через nginx. Заполнить `api/.env` по образцу
   `api/.env.example` (адрес Whisper, ключ `EXODUS_OPENROUTER_API_KEY`, строка подключения к Postgres):
   ```
   cd api && uvicorn main:app --host 127.0.0.1 --port 8000 --root-path /api
   ```
3. Установить `nginx/exodus.conf` в `/etc/nginx/sites-available/`,
   создать симлинк в `sites-enabled/`, заменить `server_name` на свой домен
   и перезагрузить nginx (`nginx -t && systemctl reload nginx`).
