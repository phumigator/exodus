"""Доступ к данным NEWS ANALYTICS: companies/news в Postgres (та же БД, что использует n8n)."""
import os

import pandas as pd
from sqlalchemy import create_engine

_engine = None


def get_engine():
    global _engine
    if _engine is None:
        # Отдельная connection string от EXODUS_DATABASE_URL (api/config.py) —
        # дашборд подключается read-only пользователем dashboard_ro, а не
        # полноправным пользователем api-сервиса.
        url = os.environ.get(
            "EXODUS_NEWS_DB_URL",
            "postgresql+psycopg2://dashboard_ro:change-me@localhost:5432/n8n",
        )
        _engine = create_engine(url)
    return _engine


def load_news(date_from=None, date_to=None, companies=None, sentiments=None):
    """Новости с привязкой к компании, с фильтрами. Только записи с распознанной компанией."""
    query = """
        SELECT n.id, n.news_date, n.title, n.content, n.source, n.sentiment,
               c.id AS company_id, c.name AS company_name
        FROM news n
        JOIN companies c ON c.id = n.company_id
        WHERE 1=1
    """
    params = {}
    if date_from:
        query += " AND n.news_date >= %(date_from)s"
        params["date_from"] = date_from
    if date_to:
        query += " AND n.news_date <= %(date_to)s"
        params["date_to"] = date_to
    if companies:
        query += " AND c.name = ANY(%(companies)s)"
        params["companies"] = list(companies)
    if sentiments:
        query += " AND n.sentiment = ANY(%(sentiments)s)"
        params["sentiments"] = list(sentiments)
    query += " ORDER BY n.news_date DESC, n.id DESC"

    return pd.read_sql(query, get_engine(), params=params)


def load_company_names():
    df = pd.read_sql("SELECT name FROM companies WHERE is_active = true ORDER BY name", get_engine())
    return df["name"].tolist()
