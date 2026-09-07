from strands import tool
import json

from .paths import DATA_DIR

@tool
def search_flights(origin: str, destination: str, date: str) -> str:
    """
    Search for available Horizon Travel flights between two airports on a given date.

    Use this tool whenever a customer asks about flight availability,
    departure times, prices, or seat availability between two cities.

    Args:
        origin      : IATA airport code for the departure airport (e.g. 'LHR', 'JFK', 'BCN')
        destination : IATA airport code for the arrival airport (e.g. 'CDG', 'MIA', 'FCO')
        date        : Travel date in YYYY-MM-DD format (e.g. '2026-03-15')

    Returns:
        A formatted summary of matching flights, or a message if none found.
    """

    with open(DATA_DIR / "flights.json") as f:
        all_flights = json.load(f)
  

    # Filter by route and date (case-insensitive)
    origin_upper = origin.upper().strip()
    dest_upper = destination.upper().strip()

    matching = [
        fl for fl in all_flights
        if fl["origin"].upper() == origin_upper
        and fl["destination"].upper() == dest_upper
        and fl["date"] == date
    ]

    if not matching:
        return (
            f"No Horizon Travel flights found from {origin_upper} to {dest_upper} "
            f"on {date}. Try an adjacent date or a different route."
        )

    lines = [f"✈️  Flights from {origin_upper} → {dest_upper} on {date}:\n"]
    for fl in matching:
        status_icon = {"SCHEDULED": "🟢", "DELAYED": "🟡", "CANCELLED": "🔴"}.get(fl["status"], "⚪")
        gate_info = f"Gate {fl['gate']}" if fl.get("gate") else "Gate TBA"
        seats = f"{fl['available_seats']} seats left" if fl["available_seats"] > 0 else "SOLD OUT"
        lines.append(
            f"  {status_icon} {fl['flight_number']}  |  {fl['departure_time']} → {fl['arrival_time']}  "
            f"|  {fl['cabin_class']}  |  ${fl['price_usd']:.2f}  |  {seats}  |  {gate_info}  |  {fl['aircraft']}"
        )

    return "\n".join(lines)