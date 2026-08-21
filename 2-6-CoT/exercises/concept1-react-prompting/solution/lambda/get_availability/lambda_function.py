import json


AVAILABILITY = {
    "r1": True,
    "r2": False,
    "r3": True,
    "r4": False,
    "r5": True,
    "r6": True,
    "r7": False,
    "r8": True,
}


def lambda_handler(event, context):
    parameters = {p["name"]: p["value"] for p in event.get("parameters", [])}
    restaurant_id = parameters.get("restaurant_id", "")

    available = AVAILABILITY.get(restaurant_id, False)
    result = {
        "restaurant_id": restaurant_id,
        "available": available,
    }

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
