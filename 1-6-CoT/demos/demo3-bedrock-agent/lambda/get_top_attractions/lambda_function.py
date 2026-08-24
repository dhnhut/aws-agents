import json


MOCK_ATTRACTIONS = {
    "london": [
        {"name": "British Museum", "type": "indoor", "family_friendly": True, "avg_visit_hours": 2},
        {"name": "Tower of London", "type": "outdoor/indoor", "family_friendly": True, "avg_visit_hours": 2.5},
        {"name": "Natural History Museum", "type": "indoor", "family_friendly": True, "avg_visit_hours": 2},
        {"name": "Hyde Park", "type": "outdoor", "family_friendly": True, "avg_visit_hours": 1.5},
        {"name": "Covent Garden", "type": "outdoor/indoor", "family_friendly": True, "avg_visit_hours": 1},
    ],
    "paris": [
        {"name": "Louvre Museum", "type": "indoor", "family_friendly": True, "avg_visit_hours": 3},
        {"name": "Eiffel Tower", "type": "outdoor/indoor", "family_friendly": True, "avg_visit_hours": 2},
        {"name": "Musée d'Orsay", "type": "indoor", "family_friendly": True, "avg_visit_hours": 2},
        {"name": "Luxembourg Gardens", "type": "outdoor", "family_friendly": True, "avg_visit_hours": 1.5},
        {"name": "Notre-Dame Cathedral", "type": "outdoor/indoor", "family_friendly": True, "avg_visit_hours": 1},
    ],
    "new york": [
        {"name": "Central Park", "type": "outdoor", "family_friendly": True, "avg_visit_hours": 2},
        {"name": "American Museum of Natural History", "type": "indoor", "family_friendly": True, "avg_visit_hours": 2.5},
        {"name": "The Metropolitan Museum of Art", "type": "indoor", "family_friendly": True, "avg_visit_hours": 3},
        {"name": "High Line", "type": "outdoor", "family_friendly": True, "avg_visit_hours": 1.5},
        {"name": "Brooklyn Bridge", "type": "outdoor", "family_friendly": True, "avg_visit_hours": 1},
    ],
}


def lambda_handler(event, context):
    parameters = {p["name"]: p["value"] for p in event.get("parameters", [])}
    city = parameters.get("city", "").lower()

    if city not in MOCK_ATTRACTIONS:
        result = {"error": f"Unknown city: '{city.title()}'. Supported cities are: London, Paris, New York."}
    else:
        result = {"city": city.title(), "attractions": MOCK_ATTRACTIONS[city]}

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
