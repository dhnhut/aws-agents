def weather_forecast(city, date):
    """
    This function takes a city and date as input and returns a weather forecast for that city on that date.
    For the purpose of this exercise, it returns a mock forecast.
    """
    # Mock weather data
    forecasts = {
        "Auckland": [
            {"date": "2026-08-12", "forecast": "Sunny", "temperature": "22°C"},
            {"date": "2026-08-13", "forecast": "Partly Cloudy", "temperature": "20°C"},
            {"date": "2026-08-14", "forecast": "Rainy", "temperature": "18°C"},
            {"date": "2026-08-15", "forecast": "Sunny", "temperature": "23°C"},
            {"date": "2026-08-16", "forecast": "Cloudy", "temperature": "21°C"},
            {"date": "2026-08-17", "forecast": "Rainy", "temperature": "19°C"}
        ],
    }
    
    for city_forecasts in forecasts.get(city, []):
        if city_forecasts["date"] == date:
            return city_forecasts
    return "Weather data not available for this city and date."