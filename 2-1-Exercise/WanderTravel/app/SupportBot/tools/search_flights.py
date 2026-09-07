import json
from typing import Optional
from strands import tool

from pydantic import BaseModel, Field, ValidationError

from .paths import DATA_DIR

class FlightSearchRequest(BaseModel):
    origin: str = Field(..., description="IATA airport code for the departure airport")
    destination: str = Field(..., description="IATA airport code for the arrival airport")
    date: str = Field(..., description="Travel date in YYYY-MM-DD format")


class FlightOption(BaseModel):
    """A single validated flight result."""
    flight_number: str = Field(description="Flight code, e.g. HZ-101")
    origin: str = Field(description="IATA departure airport code")
    destination: str = Field(description="IATA arrival airport code")
    date: str = Field(description="Flight date in YYYY-MM-DD format")
    departure_time: str = Field(description="Departure time, e.g. 08:30")
    arrival_time: str = Field(description="Arrival time, e.g. 10:45")
    price_usd: float = Field(description="Ticket price in US dollars")
    available_seats: int = Field(ge=0, description="Number of seats remaining")
    status: str = Field(description="Flight status: SCHEDULED, DELAYED, or CANCELLED")
    cabin_class: Optional[str] = Field(default=None, description="Cabin class, e.g. Economy")
    aircraft: Optional[str] = Field(default=None, description="Aircraft type, e.g. A320neo")
    gate: Optional[str] = Field(default=None, description="Departure gate, e.g. B14")


class FlightSearchResult(BaseModel):
    """Validated response containing all matching flights."""
    flights: list[FlightOption] = Field(description="List of matching flights")
    total: int = Field(description="Total number of flights found")

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
    
    try:
        # Validate input using Pydantic model
        FlightSearchRequest(origin=origin, destination=destination, date=date)
    except ValidationError as e:
        return json.dumps({"error": "Invalid search parameters", "details": str(e)})

    with open(DATA_DIR / "flights.json") as f:
        all_flights = json.load(f)
  

    # Filter by route and date (case-insensitive)
    origin_upper = origin.upper().strip()
    dest_upper = destination.upper().strip()

    matches = [
        fl for fl in all_flights
        if fl["origin"].upper() == origin_upper
        and fl["destination"].upper() == dest_upper
        and fl["date"] == date
    ]

    if not matches:
        return (
            f"No Horizon Travel flights found from {origin_upper} to {dest_upper} "
            f"on {date}. Try an adjacent date or a different route."
        )

    # --- Validate each flight record ---
    validated_flights = []
    for fl in matches:
        try:
            validated_flights.append(FlightOption.model_validate(fl))
        except ValidationError as e:
            # Skip invalid flight records but log the error
            print(f"Skipping invalid flight record: {fl}. Error: {e}")

    result = FlightSearchResult(flights=validated_flights, total=len(validated_flights))
    return result.model_dump_json(indent=2)