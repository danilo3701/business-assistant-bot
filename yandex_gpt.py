"""
YandexGPT integration helpers.
Supports graceful fallback when Yandex credentials are not configured.
"""

import logging
from typing import Optional

import aiohttp

logger = logging.getLogger(__name__)

YANDEX_URL = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
AI_DISABLED_TEXT = (
    "AI-ответы временно отключены. "
    "Используйте кнопки меню: услуги, запись, мои записи, контакты и FAQ."
)


def is_yandex_configured() -> bool:
    """Returns True if both Yandex credentials are provided."""
    from config import YANDEX_API_KEY, YANDEX_FOLDER_ID

    return bool(YANDEX_API_KEY and YANDEX_FOLDER_ID)


async def ask_yandex_gpt(
    prompt: str,
    temperature: float = 0.6,
    max_tokens: int = 500,
    system_prompt: Optional[str] = None,
) -> str:
    """Send prompt to YandexGPT or return fallback if disabled."""
    from config import YANDEX_API_KEY, YANDEX_FOLDER_ID

    if not YANDEX_API_KEY or not YANDEX_FOLDER_ID:
        logger.info("YandexGPT disabled: missing credentials")
        return AI_DISABLED_TEXT

    model_uri = f"gpt://{YANDEX_FOLDER_ID.strip()}/yandexgpt-lite"
    headers = {
        "Authorization": f"Api-Key {YANDEX_API_KEY.strip()}",
        "Content-Type": "application/json",
    }

    if system_prompt is None:
        system_prompt = (
            "Ты вежливый и дружелюбный помощник для клиентов салона красоты. "
            "Отвечай кратко и по делу. Если не знаешь ответ, предложи связаться с администратором."
        )

    data = {
        "modelUri": model_uri,
        "completionOptions": {
            "stream": False,
            "temperature": temperature,
            "maxTokens": max_tokens,
        },
        "messages": [
            {"role": "system", "text": system_prompt},
            {"role": "user", "text": prompt},
        ],
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(YANDEX_URL, headers=headers, json=data) as response:
                if response.status != 200:
                    logger.warning("YandexGPT API error: %s", response.status)
                    return "Сейчас не получилось получить AI-ответ. Попробуйте позже."

                result = await response.json()
                return result["result"]["alternatives"][0]["message"]["text"].strip()
    except Exception:
        logger.exception("YandexGPT request failed")
        return "Сейчас не получилось получить AI-ответ. Попробуйте позже."


async def generate_welcome(user_name: str) -> str:
    """Generate welcome text, fallback to static greeting if AI is disabled."""
    if not is_yandex_configured():
        return f"Здравствуйте, {user_name}!"

    prompt = (
        f"Придумай короткое приветствие для клиента {user_name}, "
        "который только что зашел в бот салона красоты. Максимум 2 предложения."
    )
    return await ask_yandex_gpt(prompt, temperature=0.8, max_tokens=100)


async def generate_response(user_message: str, context: str = "") -> str:
    """Generate assistant response with optional context."""
    prompt = (
        "Контекст:\n"
        f"{context}\n\n"
        f"Вопрос клиента: {user_message}\n\n"
        "Ответь вежливо и полезно."
    )
    return await ask_yandex_gpt(prompt, temperature=0.7)
