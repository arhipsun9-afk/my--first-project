import requests
from datetime import datetime, timezone

city = "Ноябрьск"

geo_url = "https://geocoding-api.open-meteo.com/v1/search"

try:
    response = requests.get(
        geo_url,
        params={
            "name": city,
            "count": 1,
            "language": "ru",
            "format": "json"
        },
        timeout=15
    )
    response.raise_for_status()

    data = response.json()

    if not data.get("results"):
        print("Город не найден")
        raise SystemExit

    city_data = data["results"][0]

    latitude = city_data["latitude"]
    longitude = city_data["longitude"]

    print("Город:", city)
    print("Широта:", latitude)
    print("Долгота:", longitude)

except requests.exceptions.RequestException as e:
    print("Ошибка поиска города:", e)
    raise SystemExit


weather_url = (
    "https://api.met.no/weatherapi/"
    "locationforecast/2.0/compact"
)

headers = {
    "User-Agent": "MyWeatherProject/1.0 (weather-test)"
}

try:
    weather_resp = requests.get(
        weather_url,
        params={
            "lat": latitude,
            "lon": longitude
        },
        headers=headers,
        timeout=30
    )

    weather_resp.raise_for_status()
    weather_data = weather_resp.json()

    timeseries = weather_data["properties"]["timeseries"]

    current = timeseries[0]["data"]["instant"]["details"]

    print("\nТЕКУЩАЯ ПОГОДА")
    print("Температура:", current["air_temperature"], "°C")
    print("Влажность:", current["relative_humidity"], "%")
    print("Скорость ветра:", current["wind_speed"], "м/с")

    now = datetime.now(timezone.utc)
    temperatures = []

    for item in timeseries:
        forecast_time = datetime.fromisoformat(
            item["time"].replace("Z", "+00:00")
        )

        if now <= forecast_time <= now.replace(
            hour=now.hour,
            minute=now.minute,
            second=now.second
        ).replace() + __import__("datetime").timedelta(hours=24):

            temp = item["data"]["instant"]["details"]["air_temperature"]
            temperatures.append(temp)

    if temperatures:
        print("\nПРОГНОЗ НА 24 ЧАСА")
        print("Минимальная температура:", min(temperatures), "°C")
        print("Максимальная температура:", max(temperatures), "°C")

except requests.exceptions.Timeout:
    print("Сервер погоды не ответил вовремя")

except requests.exceptions.RequestException as e:
    print("Ошибка подключения:", e)

except Exception as e:
    print("Ошибка обработки данных:", e)
