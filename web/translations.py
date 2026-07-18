"""
Словарь переводов для двуязычного интерфейса (RU/EN).

Используется через Jinja-функцию `t(key)` (регистрируется в app.py) и
экспортируется во фронтенд-JS как объект I18N (см. transcription.html) для
строк, которые генерируются динамически в transcription.js.
"""

CORRECTION_PROMPT_RU = """Ты корректор транскрипций. На вход подаётся сырой текст, распознанный речевым движком (Whisper) — в нём встречаются ошибки распознавания: неверно услышанные слова, пропущенные/лишние знаки препинания, неправильная сегментация предложений, слитые или разорванные слова. Твоя задача — только исправить эти ошибки распознавания речи, восстановив наиболее вероятный исходный текст.

Строго соблюдай:
1. Не думай вслух, не показывай рассуждения — сразу выдай финальный результат.
2. Не добавляй ничего от себя: ни новых фактов, ни пояснений, ни оценок, ни предупреждений о недостатке контекста.
3. Не суммаризируй и не сокращай — длина и структура текста должны остаться теми же, меняются только ошибочные слова и пунктуация.
4. Сохраняй исходный язык, стиль и смысл текста как есть, даже если он разговорный, незаконченный или бессвязный.
5. Если текст пустой или уже корректен — верни его без изменений.
6. Ответ должен содержать только исправленный текст, без кавычек, префиксов вроде "Исправленный текст:" и без markdown-разметки."""

CORRECTION_PROMPT_EN = """You are a transcript proofreader. The input is raw text recognized by a speech engine (Whisper) — it contains recognition errors: mishead words, missing/extra punctuation, incorrect sentence segmentation, merged or split words. Your task is only to fix these speech-recognition errors, restoring the most likely original text.

Strictly follow:
1. Do not think out loud, do not show your reasoning — output the final result directly.
2. Do not add anything of your own: no new facts, explanations, evaluations, or warnings about missing context.
3. Do not summarize or shorten the text — its length and structure must stay the same, only erroneous words and punctuation change.
4. Preserve the original language, style, and meaning of the text as is, even if it is colloquial, unfinished, or incoherent.
5. If the text is empty or already correct, return it unchanged.
6. The response must contain only the corrected text, with no quotes, no prefixes like "Corrected text:", and no markdown formatting."""

SUMMARY_PROMPT_RU = """Ты помощник, который делает краткую выжимку текста на русском языке. На вход подаётся расшифровка речи — она может содержать разговорные обороты, повторы и отступления.

Строго соблюдай:
1. Выдели только ключевые мысли, факты и решения — без второстепенных деталей и дословных повторов.
2. Не добавляй ничего от себя: ни новых фактов, ни оценок, ни выводов, которых нет в исходном тексте.
3. Сохраняй исходный смысл и порядок изложения, но формулируй кратко и связно.
4. Ответ должен содержать только саму выжимку, без markdown-разметки и префиксов вроде "Выжимка:"."""

SUMMARY_PROMPT_EN = """You are an assistant that produces a concise summary of text in English. The input is a speech transcript — it may contain colloquial phrasing, repetitions, and digressions.

Strictly follow:
1. Extract only the key ideas, facts, and decisions — without minor details or verbatim repetition.
2. Do not add anything of your own: no new facts, evaluations, or conclusions that are not present in the source text.
3. Preserve the original meaning and order of exposition, but phrase it concisely and coherently.
4. The response must contain only the summary itself, with no markdown formatting and no prefixes like "Summary:"."""

TRANSLATIONS = {
    "ru": {
        # nav
        "nav_home": "Главная",
        "nav_zcyc": "ZCYC",
        "nav_transcription": "Транскрибация",
        "nav_about": "Разработчик",
        "nav_analytics": "Аналитика",
        # index
        "index_subtitle": "Платформа аналитических и AI-сервисов",
        "badge_available": "Доступно",
        "badge_soon": "В разработке",
        "card_zcyc_title": "📊 ZCYC Dashboard",
        "card_zcyc_desc": "Кривая бескупонной доходности и анализ облигаций по ИНН.",
        "card_transcription_title": "🎙️ Транскрибация и суммаризация",
        "card_transcription_desc": "Загрузка аудио/видео, распознавание речи (Whisper) и суммаризация (OpenRouter).",
        "card_analytics_title": "📈 Аналитика",
        "card_analytics_desc": "Выгрузка и просмотр аналитики из базы данных Postgres.",
        "card_about_title": "👤 О разработчике",
        "card_about_desc": "Опыт, навыки и контакты автора этих сервисов.",
        "footer_about_link": "о разработчике",
        "footer_home_link": "на главную",
        # transcription page
        "transcription_page_title": "Транскрибация и суммаризация — Phumigator Exodus",
        "transcription_header_title": "🎙️ Транскрибация и суммаризация",
        "transcription_header_subtitle": "Загрузите аудио или видео — получите текст и краткую выжимку",
        "model_select_label": "Модель OpenRouter (коррекция, суммаризация, чат):",
        "model_gemma_label": "Google Gemma 4 31B (нестабильно)",
        "model_laguna_label": "Poolside Laguna M.1 (отключается 28.07.2026)",
        "correction_prompt_label": "Промпт коррекции распознанного текста:",
        "correction_prompt_default": CORRECTION_PROMPT_RU,
        "transcribe_btn": "Распознать речь",
        "transcript_heading": "Расшифровка",
        "download_transcript_btn": "Скачать текст",
        "summary_prompt_label": "Промпт суммаризации:",
        "summary_prompt_default": SUMMARY_PROMPT_RU,
        "summarize_btn": "Суммаризировать",
        "summary_heading": "Краткая выжимка",
        "download_summary_btn": "Скачать выжимку",
        "chat_heading": "Чат с моделью OpenRouter",
        "chat_clear_btn": "Очистить чат",
        "chat_input_placeholder": "Введите сообщение...",
        "chat_send_btn": "Отправить",
        # about page
        "about_page_title": "О разработчике — Phumigator Exodus",
        # JS-only strings (exposed via I18N object)
        "js_status_recognizing": "Распознаём речь, это может занять несколько минут...",
        "js_status_done": "Готово.",
        "js_error_recognition_prefix": "Ошибка распознавания: ",
        "js_status_summarizing": "Суммаризируем текст...",
        "js_error_summarization_prefix": "Ошибка суммаризации: ",
        "js_chat_thinking": "Модель отвечает...",
        "js_error_chat_prefix": "Ошибка чата: ",
    },
    "en": {
        # nav
        "nav_home": "Home",
        "nav_zcyc": "ZCYC",
        "nav_transcription": "Transcription",
        "nav_about": "Developer",
        "nav_analytics": "Analytics",
        # index
        "index_subtitle": "Analytics & AI services platform",
        "badge_available": "Available",
        "badge_soon": "In development",
        "card_zcyc_title": "📊 ZCYC Dashboard",
        "card_zcyc_desc": "Zero-coupon yield curve and bond analysis by tax ID (INN).",
        "card_transcription_title": "🎙️ Transcription & Summarization",
        "card_transcription_desc": "Upload audio/video, speech recognition (Whisper) and summarization (OpenRouter).",
        "card_analytics_title": "📈 Analytics",
        "card_analytics_desc": "Export and browse analytics from the Postgres database.",
        "card_about_title": "👤 About the developer",
        "card_about_desc": "Experience, skills, and contact details of this project's author.",
        "footer_about_link": "about the developer",
        "footer_home_link": "back to home",
        # transcription page
        "transcription_page_title": "Transcription & Summarization — Phumigator Exodus",
        "transcription_header_title": "🎙️ Transcription & Summarization",
        "transcription_header_subtitle": "Upload audio or video — get the text and a short summary",
        "model_select_label": "OpenRouter model (correction, summarization, chat):",
        "model_gemma_label": "Google Gemma 4 31B (unstable)",
        "model_laguna_label": "Poolside Laguna M.1 (retiring 2026-07-28)",
        "correction_prompt_label": "Correction prompt for the recognized text:",
        "correction_prompt_default": CORRECTION_PROMPT_EN,
        "transcribe_btn": "Transcribe",
        "transcript_heading": "Transcript",
        "download_transcript_btn": "Download text",
        "summary_prompt_label": "Summarization prompt:",
        "summary_prompt_default": SUMMARY_PROMPT_EN,
        "summarize_btn": "Summarize",
        "summary_heading": "Summary",
        "download_summary_btn": "Download summary",
        "chat_heading": "Chat with the OpenRouter model",
        "chat_clear_btn": "Clear chat",
        "chat_input_placeholder": "Type a message...",
        "chat_send_btn": "Send",
        # about page
        "about_page_title": "About the developer — Phumigator Exodus",
        # JS-only strings (exposed via I18N object)
        "js_status_recognizing": "Recognizing speech, this may take a few minutes...",
        "js_status_done": "Done.",
        "js_error_recognition_prefix": "Recognition error: ",
        "js_status_summarizing": "Summarizing text...",
        "js_error_summarization_prefix": "Summarization error: ",
        "js_chat_thinking": "Model is responding...",
        "js_error_chat_prefix": "Chat error: ",
    },
}

DEFAULT_LANG = "ru"
SUPPORTED_LANGS = tuple(TRANSLATIONS.keys())


def translate(lang: str, key: str) -> str:
    lang = lang if lang in TRANSLATIONS else DEFAULT_LANG
    return TRANSLATIONS[lang].get(key, TRANSLATIONS[DEFAULT_LANG].get(key, key))
