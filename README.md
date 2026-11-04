# Phumigator Exodus

Веб-платформа, объединяющая финансовые инструменты, обработку речи и браузерные игры.
Интерфейс на русском и английском, рабочая версия: [phumigator.online](http://phumigator.online).

## Разделы

| Адрес | Раздел | Что делает | Код |
|---|---|---|---|
| `/zcyc/` | ZCYC Dashboard | Кривая бескупонной доходности по данным MOEX, анализ облигаций по ИНН эмитента | `web/dash_app/` |
| `/transcription` | Транскрибация и суммаризация | Распознавание аудио/видео (Whisper), коррекция, суммаризация и чат по тексту (OpenRouter) | `web/templates/transcription.html`, `api/routers/transcription.py` |
| `/analytics/` | News Analytics | Сводка новостей по компаниям из Postgres | `web/analytics_app/` |
| `/games` | Игры | Браузерные игры на Unity WebGL с общей таблицей рекордов | `web/games.py`, `web/game_scores.py`, `web/games_builds/` |
| `/about` | О разработчике | Статическая страница | `web/templates/about.html` |

Сейчас в разделе игр есть **Seaplane (Гидроплан)**: этапы с кольцами, противниками, топливом и ремонтом,
второй уровень на закате, финал и таблица рекордов. Управление с клавиатуры или сенсорными кнопками на смартфоне.

## Архитектура

```
                        ┌────────────┐
                        │   nginx    │  reverse proxy
                        └─────┬──────┘
              ┌───────────────┴───────────────┐
              │ /                             │ /api/
     ┌────────▼─────────┐            ┌────────▼────────┐
     │   web (Flask)    │            │  api (FastAPI)  │
     │ + Dash: ZCYC,    │            │  транскрибация  │
     │   News Analytics │            │  и суммаризация │
     │ + игры, рекорды  │            └───┬─────────┬───┘
     └──┬─────┬──────┬──┘                │         │
        │     │      │                   │         │
        ▼     ▼      ▼                   ▼         ▼
     MOEX  Postgres  SQLite        whisper-bridge  OpenRouter
                     (рекорды)           │         (LLM API)
                                         ▼
                                      Whisper
```

`whisper-bridge` работает на отдельной машине рядом с контейнером Whisper и проверяет общий секрет
в запросах от `api`. Коррекция и суммаризация выполняются в `api`, потому что с машины
Whisper запросы к OpenRouter блокируются провайдером.

## Структура проекта

```
exodus/
├── web/                  # Flask: страницы, Dash-приложения, игры
│   ├── app.py
│   ├── dash_app/         # ZCYC Dashboard
│   ├── analytics_app/    # News Analytics
│   ├── games.py          # реестр игр и раздача сборок
│   ├── game_scores.py    # API таблицы рекордов
│   ├── games_builds/     # сборки Unity WebGL (.unityweb в Git LFS)
│   ├── games_data/       # база рекордов, создаётся на сервере, вне git
│   ├── translations.py   # строки интерфейса RU/EN
│   ├── templates/
│   └── static/
├── api/                  # FastAPI: транскрибация и суммаризация
│   ├── main.py
│   └── routers/transcription.py
├── whisper-bridge/       # мост к Whisper (Docker)
└── nginx/                # конфиг реверс-прокси
```

## Запуск локально

Нужны Python 3.10+ и [Git LFS](https://git-lfs.com/): без него вместо файлов сборки игры
в рабочей копии окажутся короткие текстовые ссылки, и игра не запустится.

```
git lfs install
git clone --branch FUNSIDE https://github.com/phumigator/exodus.git
cd exodus

# Сайт: http://localhost:8888
cd web && python -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python app.py

# API в другом терминале: http://localhost:8000/docs
cd api && python -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn main:app --port 8000
```

## Настройка

| Переменная | Файл | Назначение |
|---|---|---|
| `EXODUS_WHISPER_API_BASE_URL` | `api/.env` | Адрес Whisper или `whisper-bridge` |
| `EXODUS_WHISPER_SHARED_SECRET` | `api/.env` | Общий секрет для `whisper-bridge` |
| `EXODUS_OPENROUTER_API_KEY` | `api/.env` | Ключ OpenRouter |
| `EXODUS_OPENROUTER_MODEL` | `api/.env` | Модель для коррекции и суммаризации |
| `EXODUS_OPENROUTER_PROXY_URL` | `api/.env` | Прокси, если прямые запросы к OpenRouter блокируются |
| `EXODUS_CORS_ORIGINS` | `api/.env` | Разрешённые источники CORS |
| `EXODUS_NEWS_DB_URL` | `web/.env` | Подключение к Postgres для News Analytics |
| `EXODUS_API_BASE_URL` | окружение `web` | Адрес API для браузера; в проде `/api` |
| `EXODUS_GAMES_DIR` | окружение `web` | Папка сборок игр; по умолчанию `web/games_builds` |
| `EXODUS_GAMES_DB` | окружение `web` | Файл базы рекордов; по умолчанию `web/games_data/scores.sqlite` |

## Деплой на хостинге

Сервер должен получать код с установленным Git LFS (`apt install git-lfs && git lfs install`).

1. Запустить web-сервис на порту 8888. `EXODUS_API_BASE_URL` должен указывать на `/api`
   (относительный путь через nginx), иначе браузер будет обращаться к `http://localhost:8000` напрямую:
   ```
   cd web && EXODUS_API_BASE_URL=/api gunicorn --no-control-socket -w 2 -b 127.0.0.1:8888 app:app
   ```
   Флаг `--no-control-socket` нужен для новых версий gunicorn: без него gunicorn пытается создать управляющий
   сокет в домашней папке пользователя и пишет ошибку в лог, если у пользователя нет туда доступа.
2. Запустить api-сервис на порту 8000 с `--root-path /api`, чтобы ссылки и openapi-схема учитывали префикс,
   под которым сервис доступен через nginx. Заполнить `api/.env` по образцу `api/.env.example`:
   ```
   cd api && uvicorn main:app --host 127.0.0.1 --port 8000 --root-path /api
   ```
3. Дать процессу сайта права на запись в папку рекордов. Права нужны на саму папку, потому что SQLite
   создаёт рядом с базой временный журнал:
   ```
   install -d -o www-data -g www-data -m 750 web/games_data
   ```
4. Установить `nginx/exodus.conf` в `/etc/nginx/sites-available/`, создать симлинк в `sites-enabled/`,
   заменить `server_name` на свой домен и перезагрузить nginx (`nginx -t && systemctl reload nginx`).

Обновление: `git pull`, затем при запуске команд от root `chown -R www-data:www-data` на папку проекта и
перезапуск изменившегося сервиса. Если после обновления игра не загружается, проверьте, что файл
`web/games_builds/seaplane/Build/FlightBounty.data.unityweb` весит десятки мегабайт, а не около 130 байт.

## Браузерные игры (Unity WebGL)

Раздел `/games` показывает список игр из `web/games.py`, страница игры находится по адресу `/games/<slug>`.
Пока сборки нет, на странице показывается заглушка.

Сборка лежит в git в том виде, в каком её выдаёт Unity: `web/games_builds/<slug>/`
(`Build/`, `TemplateData/`, `index.html`). Файлы `.unityweb` хранятся в Git LFS, поэтому перед коммитом
новой сборки на машине должен быть установлен `git-lfs`, иначе они уйдут в обычный git.
Сборку отдаёт сам Flask под `/games-build/<slug>/…`.

Сборка собрана с Gzip + Decompression Fallback, поэтому особые заголовки в nginx не нужны.
Если пересобрать её с Brotli/Gzip без fallback (`.br`/`.gz`), Flask сам выставит `Content-Encoding`,
но Brotli в браузере работает только по HTTPS.

### Таблица рекордов

`GET /games-api/<slug>/scores` возвращает лучшие 10 результатов, а
`POST /games-api/<slug>/scores` с телом `{"name": "...", "coins": 123}` добавляет результат и возвращает таблицу.

На игру хранится до 100 лучших результатов. База не входит в git, поэтому обновление сайта её не затирает.
Результат присылает сама игра, так что подделать его можно.

### Новая игра

Добавить slug в `GAMES` (`web/games.py`) и строки `game_<slug>_title` / `game_<slug>_desc` в `web/translations.py`.
