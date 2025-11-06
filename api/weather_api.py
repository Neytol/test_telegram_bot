import asyncio
import logging
import time
from dotenv import load_dotenv
import os
logger = logging.getLogger(__name__)
load_dotenv()
TOKEN = os.getenv("OPENWEATHER_API_KEY")

import aiohttp


BASE_URL = "http://api.openweathermap.org/data/2.5/weather"

weather_cache = {}
CACHE_DURATION = 300

async def get_weather(city: str) -> str:
    city_key = city.strip().lower()

    current_time = time.time()

    if city_key in weather_cache:
        cached = weather_cache[city_key]
        if current_time - cached["timestamp"] < CACHE_DURATION:
            logger.info("Взял данные из кэша")
            logger.info(f"До обновления данных {int(CACHE_DURATION - (current_time - cached["timestamp"]))} секунд")
        return f"Погода в {cached['city_name']}:\n{cached['temperature']}°C, {cached['description']}"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                BASE_URL, params={
            'q': city,
            'appid': TOKEN,
            'units': 'metric',
            'lang':'ru',
            }
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    temperature = data['main']['temp']
                    description = data['weather'][0]['description']
                    city_name = data['name']
                    weather_cache[city_key] = {
                        "temperature": temperature,
                        "description": description,
                        "city_name": city_name,
                        "timestamp": current_time
                    }
                    return f"Погода в {city_name}:\n {temperature}°C, {description}"
                elif response.status == 404:
                    return "Город не найден"
                else:
                    return "Ошибка при получении погоды"

    except Exception as e:
        logger.error(f"Ошибка в get_weather для города '{city}': {e}")
        return "⚠️ Не удалось получить погоду. Попробуй позже."


