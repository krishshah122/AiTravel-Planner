import os
import json
import requests
from langchain_tavily import TavilySearch

# ------------------ OpenStreetMap Wrapper (REPLACES Google Places) ------------------

class OpenStreetMapPlaceSearchTool:
    def __init__(self):
        self.api_url = "https://nominatim.openstreetmap.org/search"
        self.headers = {
            "User-Agent": "TripAgentBot/1.0 (your_email@example.com)"  # Required by OSM
        }

    def _osm_search(self, query: str):
        params = {
            "q": query,
            "format": "json",
            "limit": 5
        }
        response = requests.get(self.api_url, params=params, headers=self.headers)
        if response.status_code == 200:
            return response.json()
        return {"error": "Failed to fetch results from OpenStreetMap"}

    def google_search_attractions(self, place: str) -> dict:
        return self._osm_search(f"top tourist attractions near {place}")

    def google_search_restaurants(self, place: str) -> dict:
        return self._osm_search(f"restaurants and eateries in {place}")

    def google_search_activity(self, place: str) -> dict:
        return self._osm_search(f"popular activities and things to do in {place}")

    def google_search_transportation(self, place: str) -> dict:
        return self._osm_search(f"transportation options in {place}")

# ------------------ Tavily Search Tool (Unchanged) ------------------

class TavilyPlaceSearchTool:
    def __init__(self):
        pass

    def tavily_search_attractions(self, place: str) -> dict:
        tavily_tool = TavilySearch(topic="general", include_answer="advanced")
        result = tavily_tool.invoke({"query": f"top attractive places in and around {place}"})
        if isinstance(result, dict) and result.get("answer"):
            return result["answer"]
        return result

    def tavily_search_restaurants(self, place: str) -> dict:
        tavily_tool = TavilySearch(topic="general", include_answer="advanced")
        result = tavily_tool.invoke({"query": f"what are the top 10 restaurants and eateries in and around {place}."})
        if isinstance(result, dict) and result.get("answer"):
            return result["answer"]
        return result

    def tavily_search_activity(self, place: str) -> dict:
        tavily_tool = TavilySearch(topic="general", include_answer="advanced")
        result = tavily_tool.invoke({"query": f"activities in and around {place}"})
        if isinstance(result, dict) and result.get("answer"):
            return result["answer"]
        return result

    def tavily_search_transportation(self, place: str) -> dict:
        tavily_tool = TavilySearch(topic="general", include_answer="advanced")
        result = tavily_tool.invoke({"query": f"What are the different modes of transportations available in {place}"})
        if isinstance(result, dict) and result.get("answer"):
            return result["answer"]
        return result