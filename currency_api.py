import  aiohttp
from datetime import date



BASE_URL = "https://www.cbr-xml-daily.ru/daily_json.js"

cache_data_usd = None
cache_data_eur = None
cache_date = None


async  def get_currency(user_text: str):
    global cache_data_usd, cache_data_eur, cache_date

    today = date.today()


    if cache_data_eur and cache_data_usd and cache_date == today:
        if user_text == "Курс доллара 💵":
            return cache_data_usd
        elif user_text == "Курс евро 💶":
            return cache_data_eur

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(BASE_URL) as response:
                if response.status == 200:
                    data = await response.json(content_type=None)
                if user_text == "Курс доллара 💵":
                    usd = f"💵 Курс доллара: {round(data['Valute']['USD']['Value'])}₽"
                    cache_data_usd = usd
                    cache_date = today
                    return usd
                elif user_text == "Курс евро 💶":
                    eur = f"💶 Курс евро: {round(data['Valute']['EUR']['Value'])}₽"
                    cache_data_eur = eur
                    cache_date = today
                    return eur

                elif response.status == 404:
                    return "В данный момент информация о курсе валют не доступна."
                else:
                    return "Не возможно получить информацию о курсе валют."

    except Exception as e:
        return f"Ошибка {e}"




