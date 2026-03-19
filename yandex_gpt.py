"""
Модуль для работы с YandexGPT API
Содержит функции для отправки запросов и генерации ответов
"""

import aiohttp
import logging
from typing import Optional
from config import YANDEX_API_KEY, YANDEX_FOLDER_ID

# Настройка логирования
logger = logging.getLogger(__name__)

# URL для YandexGPT API
YANDEX_URL = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"

async def ask_yandex_gpt(
    prompt: str, 
    temperature: float = 0.6,
    max_tokens: int = 500,
    system_prompt: Optional[str] = None
) -> str:
    """
    Отправляет запрос к YandexGPT и возвращает ответ
    
    Аргументы:
        prompt: текст запроса пользователя
        temperature: температура генерации (0.0 - 1.0)
        max_tokens: максимальное количество токенов в ответе
        system_prompt: системный промпт (если нужен)
    
    Возвращает:
        str: ответ от нейросети или сообщение об ошибке
    """
    
    # Заголовки запроса
    headers = {
        "Authorization": f"Api-Key {YANDEX_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # Формируем сообщения
    messages = []
    
    # Системный промпт по умолчанию для бизнес-ассистента
    if system_prompt is None:
        system_prompt = (
            "Ты вежливый и дружелюбный помощник для клиентов салона красоты. "
            "Отвечай кратко, по делу, но приветливо. "
            "Если не знаешь ответа, предложи связаться с администратором."
        )
    
    messages.append({
        "role": "system",
        "text": system_prompt
    })
    
    messages.append({
        "role": "user",
        "text": prompt
    })
    
    # Тело запроса
    data = {
        "modelUri": f"gpt://{YANDEX_FOLDER_ID}/yandexgpt-lite",
        "completionOptions": {
            "stream": False,
            "temperature": temperature,
            "maxTokens": max_tokens
        },
        "messages": messages
    }
    
    try:
        # Отправляем запрос
        async with aiohttp.ClientSession() as session:
            async with session.post(YANDEX_URL, headers=headers, json=data) as response:
                
                if response.status == 200:
                    result = await response.json()
                    answer = result['result']['alternatives'][0]['message']['text']
                    return answer.strip()
                
                else:
                    error_text = await response.text()
                    logger.error(f"YandexGPT API error: {response.status} - {error_text}")
                    return "❌ Извините, техническая ошибка. Попробуйте позже."
    
    except aiohttp.ClientError as e:
        logger.error(f"Network error: {e}")
        return "❌ Ошибка соединения. Проверьте интернет."
    
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return "❌ Не удалось получить ответ. Попробуйте позже."

async def generate_welcome(user_name: str) -> str:
    """
    Генерирует персонализированное приветствие для клиента
    
    Аргументы:
        user_name: имя пользователя
    
    Возвращает:
        str: тёплое приветствие
    """
    prompt = (
        f"Придумай короткое, тёплое приветствие для клиента {user_name}, "
        f"который только что зашёл в бота салона красоты. "
        f"Максимум 2 предложения. Будь дружелюбным."
    )
    return await ask_yandex_gpt(prompt, temperature=0.8, max_tokens=100)

async def generate_response(user_message: str, context: str = "") -> str:
    """
    Упрощённая функция для ответов на вопросы клиентов
    
    Аргументы:
        user_message: сообщение пользователя
        context: дополнительный контекст (например, информация о салоне)
    
    Возвращает:
        str: ответ от нейросети
    """
    prompt = f"""
Контекст (информация о салоне):
{context}

Вопрос клиента: {user_message}

Ответь вежливо и полезно. Если вопрос не относится к услугам салона, 
предложи связаться с администратором.
"""
    return await ask_yandex_gpt(prompt, temperature=0.7)