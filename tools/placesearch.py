import os
from utils.placesearch import OpenStreetMapPlaceSearchTool, TavilyPlaceSearchTool
from typing import List
from langchain.tools import tool
from dotenv import load_dotenv

class PlaceSearchTool:
    def __init__(self):
        load_dotenv()
        self.osm_places_search = OpenStreetMapPlaceSearchTool()  # ✅ Replaces Google
        self.tavily_search = TavilyPlaceSearchTool()
        self.place_search_tool_list = self._setup_tools()

    def _setup_tools(self) -> List:
        """Setup all tools for the place search tool"""

        @tool
        def search_attractions(place: str) -> str:
            """Search attractions of a place"""
            try:
                attraction_result = self.osm_places_search.google_search_attractions(place)
                if attraction_result:
                    return f"Attractions in {place} from OpenStreetMap: {attraction_result}"
            except Exception as e:
                tavily_result = self.tavily_search.tavily_search_attractions(place)
                return f"OSM search failed due to {e}.\nFallback Tavily results: {tavily_result}"

        @tool
        def search_restaurants(place: str) -> str:
            """Search restaurants of a place"""
            try:
                restaurants_result = self.osm_places_search.google_search_restaurants(place)
                if restaurants_result:
                    return f"Restaurants in {place} from OpenStreetMap: {restaurants_result}"
            except Exception as e:
                tavily_result = self.tavily_search.tavily_search_restaurants(place)
                return f"OSM search failed due to {e}.\nFallback Tavily results: {tavily_result}"

        @tool
        def search_activities(place: str) -> str:
            """Search activities of a place"""
            try:
                activities_result = self.osm_places_search.google_search_activity(place)
                if activities_result:
                    return f"Activities in {place} from OpenStreetMap: {activities_result}"
            except Exception as e:
                tavily_result = self.tavily_search.tavily_search_activity(place)
                return f"OSM search failed due to {e}.\nFallback Tavily results: {tavily_result}"

        @tool
        def search_transportation(place: str) -> str:
            """Search transportation options of a place"""
            try:
                transport_result = self.osm_places_search.google_search_transportation(place)
                if transport_result:
                    return f"Transportation options in {place} from OpenStreetMap: {transport_result}"
            except Exception as e:
                tavily_result = self.tavily_search.tavily_search_transportation(place)
                return f"OSM search failed due to {e}.\nFallback Tavily results: {tavily_result}"

        return [
            search_attractions,
            search_restaurants,
            search_activities,
            search_transportation
        ]
