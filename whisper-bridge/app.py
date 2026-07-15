"""
Whisper-мост: принимает аудио от VPS (Exodus API), проверяет общий секрет,
пересылает файл во внутренний Whisper-контейнер, прогоняет распознанный
текст через OpenRouter для исправления грамматики/смысла (не суммаризация)
и возвращает результат в том же формате, что отдаёт сам Whisper.
"""
import httpx
from fastapi import FastAPI, File, Header, HTTPException, Query, UploadFile

from config import settings

app = FastAPI(title="Exodus Whisper Bridge")

CORRECTION_PROMPT = (
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


def _check_token(x_internal_token: str | None) -> None:
    if not settings.shared_secret:
        raise HTTPException(status_code=500, detail="BRIDGE_SHARED_SECRET не задан")
    if x_internal_token != settings.shared_secret:
        raise HTTPException(status_code=401, detail="Неверный или отсутствующий X-Internal-Token")


async def _correct_text(raw_text: str) -> str:
    if not raw_text.strip() or not settings.openrouter_api_key:
        return raw_text

    payload = {
        "model": settings.openrouter_model,
        "messages": [
            {"role": "system", "content": CORRECTION_PROMPT},
            {"role": "user", "content": raw_text},
        ],
    }
    headers = {"Authorization": f"Bearer {settings.openrouter_api_key}"}

    async with httpx.AsyncClient(timeout=120, trust_env=False) as client:
        try:
            response = await client.post(
                f"{settings.openrouter_base_url}/chat/completions",
                json=payload,
                headers=headers,
            )
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]
        except (httpx.HTTPError, KeyError, IndexError, TypeError):
            # Коррекция необязательна: при сбое OpenRouter отдаём сырой текст,
            # чтобы транскрибация не падала целиком из-за внешнего сервиса.
            return raw_text


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/asr")
async def asr(
    audio_file: UploadFile = File(...),
    output: str = Query("json"),
    x_internal_token: str | None = Header(None),
):
    _check_token(x_internal_token)

    async with httpx.AsyncClient(timeout=600, trust_env=False) as client:
        files = {
            "audio_file": (audio_file.filename, await audio_file.read(), audio_file.content_type)
        }
        try:
            response = await client.post(
                f"{settings.whisper_internal_url}/asr",
                params={"output": "json"},
                files=files,
            )
            response.raise_for_status()
        except httpx.HTTPError as exc:
            raise HTTPException(status_code=502, detail=f"Внутренний Whisper недоступен: {exc}")

    raw = response.json()
    corrected_text = await _correct_text(raw.get("text", ""))
    return {"text": corrected_text}
