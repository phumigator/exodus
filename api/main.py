"""
FastAPI-сервис Phumigator Exodus: транскрибация/суммаризация.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import settings
from routers import transcription

app = FastAPI(title="Phumigator Exodus API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(transcription.router)


@app.get("/health")
async def health():
    return {"status": "ok"}
