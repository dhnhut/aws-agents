from strands import tool
import json

from .paths import DATA_DIR

@tool
def search_hotels(city: str, max_price_usd: float = 999.0) -> str:
    """
    Search for available hotels in a city, with an optional maximum nightly price.

    Use this tool when a customer asks about accommodation options,
    hotel prices, amenities, room types, or check-in/check-out policies.

    Args:
        city          : Destination city name (e.g. 'Barcelona', 'Tokyo', 'Dubai', 'Rome')
        max_price_usd : Optional maximum price per night in USD. Defaults to no limit (999).

    Returns:
        A formatted list of matching hotels with prices, ratings, and amenities.
    """

    try:
        with open(DATA_DIR / "hotels.json") as f:
            all_hotels = json.load(f)
    except FileNotFoundError:
        return "Error: Hotel database is temporarily unavailable. Please try again."

    # Filter by city (case-insensitive) and price
    city_lower = city.lower().strip()
    matching = [
        h for h in all_hotels
        if h["city"].lower() == city_lower
        and h["available"]
        and h["price_per_night_usd"] <= max_price_usd
    ]

    if not matching:
        return (
            f"No available hotels found in {city} under ${max_price_usd:.0f}/night. "
            f"Try increasing your budget or check a nearby city."
        )

    stars_map = {5: "⭐⭐⭐⭐⭐", 4: "⭐⭐⭐⭐", 3: "⭐⭐⭐", 2: "⭐⭐", 1: "⭐"}
    lines = [f"🏨  Available hotels in {city.title()} (max ${max_price_usd:.0f}/night):\n"]

    for h in sorted(matching, key=lambda x: x["price_per_night_usd"]):
        amenity_summary = ", ".join(h["amenities"][:3])  # show first 3 amenities
        lines.append(
            f"  {stars_map.get(h['star_rating'], '')} {h['name']}\n"
            f"     ${h['price_per_night_usd']:.0f}/night  |  Rooms: {', '.join(h['room_types'])}\n"
            f"     Amenities: {amenity_summary}  |  Check-in: {h['check_in_time']}\n"
            f"     Cancellation: {h['cancellation_policy']}\n"
        )

    return "\n".join(lines)