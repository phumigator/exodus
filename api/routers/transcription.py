"""
Транскрибация, коррекция и суммаризация загруженного аудио/видео.

Аудио передаётся в Whisper (распознавание речи, whisper-bridge на локальной
машине разработчика), коррекция и суммаризация текста — в OpenRouter (внешний
LLM API). Коррекция намеренно не делается в whisper-bridge: прямые запросы к
OpenRouter с той машины блокируются провайдером, а отсюда (VPS) — нет.
"""
import asyncio

import httpx
from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel

from config import settings

router = APIRouter(prefix="/transcription", tags=["transcription"])


DEFAULT_SUMMARY_PROMPT = "Ты помощник, который делает краткую выжимку текста на русском языке."
DEFAULT_CORRECTION_PROMPT = (
    "Ты корректор транскрипций. На вход подаётся сырой текст, распознанный "
    "речевым движком (Whisper) — в нём встречаются ошибки распознавания: "
    "неверно услышанные слова, пропущенные/лишние знаки препинания, "
    "неправильная сегментация предложений, слитые или разорванные слова. "
    "Твоя задача — только исправить эти ошибки распознавания речи, "
    "восстановив наиболее вероятный исходный текст.\n\n"
    "Строго соблюдай:\n"
    "1. Не думай вслух, не показывай рассуждения — сразу выдай финальный результат.\n"
    "2. Не добавляй ничего от себя: ни новых фактов, ни пояснений, ни оценок, "
    "ни предупреждений о недостатке контекста.\n"
    "3. Не суммаризируй и не сокращай — длина и структура текста должны "
    "остаться теми же, меняются только ошибочные слова и пунктуация.\n"
    "4. Сохраняй исходный язык, стиль и смысл текста как есть, даже если он "
    "разговорный, незаконченный или бессвязный.\n"
    "5. Если текст пустой или уже корректен — верни его без изменений.\n"
    "6. Ответ должен содержать только исправленный текст, без кавычек, "
    "префиксов вроде \"Исправленный текст:\" и без markdown-разметки."
)


class SummarizeRequest(BaseModel):
    text: str
    model: str | None = None
    prompt: str | None = None


class CorrectRequest(BaseModel):
    text: str
    model: str | None = None
    prompt: str | None = None


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    messages: list[ChatMessage]
    model: str | None = None


async def _call_openrouter(messages: list[dict], model: str | None) -> str:
    """Отправляет список сообщений в OpenRouter (chat completions) и возвращает ответ модели."""
    if not settings.openrouter_api_key:
        raise HTTPException(status_code=500, detail="EXODUS_OPENROUTER_API_KEY не задан")

    payload = {
        "model": model or settings.openrouter_model,
        "messages": messages,
    }
    headers = {
        "Authorization": f"Bearer {settings.openrouter_api_key}",
        "HTTP-Referer": settings.openrouter_site_url,
        "X-Title": settings.openrouter_app_name,
    }

    # trust_env=False: игнорируем системные HTTP_PROXY/ALL_PROXY — на машине
    # ALL_PROXY использует схему "socks://", которую httpx не распознаёт,
    # и AsyncClient падает ещё до подключения. Прокси для OpenRouter (если нужен,
    # т.к. прямые запросы блокируются) передаём явно через настройки.
    async with httpx.AsyncClient(
        timeout=120, trust_env=False, proxy=settings.openrouter_proxy_url
    ) as client:
        # Бесплатные модели делят лимиты между всеми пользователями OpenRouter и
        # периодически ловят транзиентную нехватку мощности у провайдера (см. память
        # проекта) — как HTTP 404/429, так и HTTP 200 с телом вида {"error": {...}}
        # (например "Upstream error from Nvidia: ResourceExhausted"). Окно ретраев
        # ~30 сек (5 попыток, паузы 3/6/9/12 сек) на оба варианта сбоя.
        max_attempts = 5
        data = None
        for attempt in range(max_attempts):
            response = await client.post(
                f"{settings.openrouter_base_url}/chat/completions",
                json=payload,
                headers=headers,
            )
            is_last = attempt == max_attempts - 1
            if response.status_code in (404, 429) and not is_last:
                await asyncio.sleep(3 * (attempt + 1))
                continue

            try:
                response.raise_for_status()
            except httpx.HTTPError as exc:
                if is_last:
                    raise HTTPException(status_code=502, detail=f"OpenRouter API error: {exc}")
                await asyncio.sleep(3 * (attempt + 1))
                continue

            data = response.json()
            if "error" in data and not is_last:
                await asyncio.sleep(3 * (attempt + 1))
                continue
            break

    try:
        return data["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError):
        raise HTTPException(status_code=502, detail=f"Неожиданный ответ OpenRouter: {data}")


@router.post("/transcribe")
async def transcribe(file: UploadFile = File(...)):
    """Отправляет файл в Whisper API и возвращает распознанный текст (без коррекции)."""
    async with httpx.AsyncClient(timeout=1800, trust_env=False) as client:
        files = {"audio_file": (file.filename, await file.read(), file.content_type)}
        headers = {"X-Internal-Token": settings.whisper_shared_secret}
        try:
            response = await client.post(
                f"{settings.whisper_api_base_url}/asr",
                params={"output": "json"},
                files=files,
                headers=headers,
            )
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            # Мост ответил (жив), но отклонил запрос — например, аудиофайл нельзя
            # декодировать, или неверный токен. Пробрасываем его настоящий статус
            # и текст ошибки вместо общего 502, иначе реальная причина теряется.
            try:
                detail = exc.response.json().get("detail", exc.response.text)
            except ValueError:
                detail = exc.response.text
            raise HTTPException(status_code=exc.response.status_code, detail=detail)
        except httpx.HTTPError as exc:
            raise HTTPException(status_code=502, detail=f"Whisper API error: {exc}")

    return response.json()


@router.post("/correct")
async def correct(request: CorrectRequest):
    """Исправляет ошибки распознавания речи в тексте через OpenRouter."""
    messages = [
        {"role": "system", "content": request.prompt or DEFAULT_CORRECTION_PROMPT},
        {"role": "user", "content": request.text},
    ]
    corrected = await _call_openrouter(messages, request.model)
    return {"corrected_text": corrected}


@router.post("/summarize")
async def summarize(request: SummarizeRequest):
    """Суммаризирует текст через OpenRouter."""
    messages = [
        {
            "role": "system",
            "content": request.prompt or DEFAULT_SUMMARY_PROMPT,
        },
        {
            "role": "user",
            "content": f"Сделай краткую выжимку следующего текста:\n\n{request.text}",
        },
    ]
    summary = await _call_openrouter(messages, request.model)
    return {"summary": summary}


@router.post("/chat")
async def chat(request: ChatRequest):
    """Пересылает историю диалога в OpenRouter и возвращает ответ модели."""
    messages = [m.model_dump() for m in request.messages]
    reply = await _call_openrouter(messages, request.model)
    return {"role": "assistant", "content": reply}
