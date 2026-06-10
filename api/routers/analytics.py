"""
Выгрузка аналитики из Postgres, работающей на удалённом сервере.
"""
import asyncpg
from fastapi import APIRouter, HTTPException

from config import settings

router = APIRouter(prefix="/analytics", tags=["analytics"])


async def get_connection():
    try:
        return await asyncpg.connect(settings.database_url)
    except OSError as exc:
        raise HTTPException(status_code=502, detail=f"Database connection error: {exc}")


@router.get("/tables")
async def list_tables():
    """Возвращает список таблиц в публичной схеме."""
    conn = await get_connection()
    try:
        rows = await conn.fetch(
            "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"
        )
    finally:
        await conn.close()

    return {"tables": [row["table_name"] for row in rows]}


@router.get("/query")
async def run_query(table: str, limit: int = 100):
    """Возвращает первые `limit` строк указанной таблицы."""
    conn = await get_connection()
    try:
        exists = await conn.fetchval(
            "SELECT 1 FROM information_schema.tables "
            "WHERE table_schema = 'public' AND table_name = $1",
            table,
        )
        if not exists:
            raise HTTPException(status_code=404, detail=f"Unknown table: {table}")

        rows = await conn.fetch(f'SELECT * FROM "{table}" LIMIT $1', limit)
    finally:
        await conn.close()

    return {"rows": [dict(row) for row in rows]}
