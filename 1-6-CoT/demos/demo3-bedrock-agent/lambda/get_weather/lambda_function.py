import json


MOCK_WEATHER = {
    "london": {
        "condition": "Light rain in the morning, clearing to partly cloudy by afternoon",
        "temperature_celsius": 11,
        "wind_mph": 12,
        "recommendation": "Bring a light jacket and umbrella for the morning",
    },
    "paris": {
        "condition": "Mostly sunny with light clouds",
        "temperature_celsius": 14,
        "wind_mph": 8,
        "recommendation": "Great day to be outdoors",
    },
    "new york": {
        "condition": "Clear skies, cold",
        "temperature_celsius": 5,
        "wind_mph": 15,
        "recommendation": "Dress warmly, especially in the wind",
    },
}


def lambda_handler(event, context):
    parameters = {p["name"]: p["value"] for p in event.get("parameters", [])}
    city = parameters.get("city", "").lower()
    date = parameters.get("date", "")

    if city not in MOCK_WEATHER:
        result = {"error": f"Unknown city: '{city.title()}'. Supported cities are: London, Paris, New York."}
    else:
        result = MOCK_WEATHER[city]
        result["city"] = city.title()
        result["date"] = date

    return {
        "messageVersion": "1.0",
        "response": {
            "actionGroup": event["actionGroup"],
            "function": event["function"],
            "functionResponse": {
                "responseBody": {
                    "TEXT": {
                        "body": json.dumps(result)
                    }
                }
            },
        },
    }
