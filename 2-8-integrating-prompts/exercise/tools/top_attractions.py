def top_attractions(city):
    """
    This function takes a city as input and returns a list of top attractions for that city.
    For the purpose of this exercise, it returns a mock list of attractions.
    """
    # Mock attractions data
    attractions = {
        "Auckland": [
            {"place": "Waiheke Island", "type": "outdoor"},
            {"place": "Sky Tower", "type": "indoor"},
            {"place": "Auckland War Memorial Museum", "type": "indoor"},
            {"place": "Auckland Domain", "type": "outdoor"},
            {"place": "Kelly Tarlton's Sea Life Aquarium", "type": "indoor"},
            {"place": "Rangitoto Island", "type": "outdoor"},],
    }

    return attractions.get(city, [{"place": "Attractions data not available for this city."}])