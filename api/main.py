"""
FastAPI-сервис Exodus: транскрибация/суммаризация и выгрузка аналитики.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .routers import transcription, analytics

app = FastAPI(title="Exodus API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(transcription.router)
app.include_router(analytics.router)


@app.get("/health")
async def health():
    return {"status": "ok"}
