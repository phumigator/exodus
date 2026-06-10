"""
Транскрибация и суммаризация загруженного аудио/видео.

Аудио передаётся в Whisper (распознавание речи), полученный текст —
в Ollama (суммаризация), оба сервиса работают на удалённом сервере.
"""
import httpx
from fastapi import APIRouter, UploadFile, File, HTTPException

from ..config import settings

router = APIRouter(prefix="/transcription", tags=["transcription"])


@router.post("/transcribe")
async def transcribe(file: UploadFile = File(...)):
    """Отправляет файл в Whisper API и возвращает распознанный текст."""
    async with httpx.AsyncClient(timeout=600) as client:
        files = {"file": (file.filename, await file.read(), file.content_type)}
        try:
            response = await client.post(
                f"{settings.whisper_api_base_url}/asr",
                files=files,
            )
            response.raise_for_status()
        except httpx.HTTPError as exc:
            raise HTTPException(status_code=502, detail=f"Whisper API error: {exc}")

    return response.json()


@router.post("/summarize")
async def summarize(text: str, model: str = "llama3"):
    """Отправляет текст в Ollama и возвращает суммаризацию."""
    payload = {
        "model": model,
        "prompt": f"Сделай краткую выжимку следующего текста:\n\n{text}",
        "stream": False,
    }
    async with httpx.AsyncClient(timeout=600) as client:
        try:
            response = await client.post(
                f"{settings.remote_api_base_url}/api/generate",
                json=payload,
            )
            response.raise_for_status()
        except httpx.HTTPError as exc:
            raise HTTPException(status_code=502, detail=f"Ollama API error: {exc}")

    return response.json()
