"""Доступ к данным NEWS ANALYTICS: companies/news в Postgres (та же БД, что использует n8n)."""
import os

import pandas as pd
from sqlalchemy import create_engine

_engine = None

# `source` хранится то полным URL статьи, то голым доменом — фильтруем и
# группируем по домену без схемы и "www." (ср. _source_link в callbacks.py).
# Пустой/NULL source сворачивается в '' — чтобы такие записи тоже были видны в фильтре.
_SOURCE_DOMAIN_SQL = r"COALESCE(regexp_replace(btrim(n.source), '^(https?://)?(www\.)?([^/?#]+).*$', '\3'), '')"

# Значение пункта "без источника" в фильтре (Dropdown не дружит с пустой строкой).
EMPTY_SOURCE = "__empty__"

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


def _filters(date_from=None, date_to=None, companies=None, sentiments=None, sources=None):
    """WHERE-условия для news n JOIN companies c и их параметры."""
    clauses, params = [], {}
    if date_from:
        clauses.append("n.news_date >= %(date_from)s")
        params["date_from"] = date_from
    if date_to:
        clauses.append("n.news_date <= %(date_to)s")
        params["date_to"] = date_to
    if companies:
        clauses.append("c.name = ANY(%(companies)s)")
        params["companies"] = list(companies)
    if sentiments:
        clauses.append("n.sentiment = ANY(%(sentiments)s)")
        params["sentiments"] = list(sentiments)
    if sources:
        clauses.append(f"{_SOURCE_DOMAIN_SQL} = ANY(%(sources)s)")
        params["sources"] = ["" if s == EMPTY_SOURCE else s for s in sources]
    return "".join(f" AND {c}" for c in clauses), params


def load_news(date_from=None, date_to=None, companies=None, sentiments=None, sources=None):
    """Новости с привязкой к компании, с фильтрами. Только записи с распознанной компанией."""
    where, params = _filters(date_from, date_to, companies, sentiments, sources)
    query = f"""
        SELECT n.id, n.news_date, n.title, n.content, n.source, n.sentiment,
               c.id AS company_id, c.name AS company_name
        FROM news n
        JOIN companies c ON c.id = n.company_id
        WHERE 1=1{where}
        ORDER BY n.news_date DESC, n.id DESC
    """
    return pd.read_sql(query, get_engine(), params=params)

def load_company_names():
    df = pd.read_sql("SELECT name FROM companies WHERE is_active = true ORDER BY name", get_engine())
    return df["name"].tolist()


def load_source_counts(date_from=None, date_to=None, companies=None, sentiments=None):
    """Все домены источников (включая пустые и кривые) с числом новостей
    при текущих фильтрах — чтобы аномалии в `source` сразу были видны."""
    where, params = _filters(date_from, date_to, companies, sentiments)
    query = f"""
        SELECT {_SOURCE_DOMAIN_SQL} AS domain, count(*) AS cnt
        FROM news n
        JOIN companies c ON c.id = n.company_id
        WHERE 1=1{where}
        GROUP BY 1
        ORDER BY 2 DESC, 1
    """
    return pd.read_sql(query, get_engine(), params=params)
