import requests

class WeatherForecastTool:
    def __init__(self, api_key: str = None):
        self.api_key = api_key
        self.base_url = "https://api.open-meteo.com/v1"
        self.geo_url = "https://geocoding-api.open-meteo.com/v1/search"

    def _geocode(self, place: str) -> dict:
        params = {
            "name": place,
            "count": 1,
            "language": "en",
            "format": "json",
        }
        response = requests.get(self.geo_url, params=params, timeout=10)
        if response.status_code != 200:
            return {}
        data = response.json()
        if not data.get("results"):
            return {}
        return data["results"][0]

    def get_current_weather(self, place: str) -> dict:
        """Get current weather for a place using Open-Meteo"""
        location = self._geocode(place)
        if not location:
            return {}

        params = {
            "latitude": location["latitude"],
            "longitude": location["longitude"],
            "current_weather": True,
            "timezone": "auto",
        }
        url = f"{self.base_url}/forecast"
        response = requests.get(url, params=params, timeout=10)
        return response.json() if response.status_code == 200 else {}
    
    def get_forecast_weather(self, place: str) -> dict:
        """Get weather forecast for a place using Open-Meteo"""
        location = self._geocode(place)
        if not location:
            return {}

        params = {
            "latitude": location["latitude"],
            "longitude": location["longitude"],
            "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum,weathercode",
            "timezone": "auto",
        }
        url = f"{self.base_url}/forecast"
        response = requests.get(url, params=params, timeout=10)
        return response.json() if response.status_code == 200 else {}