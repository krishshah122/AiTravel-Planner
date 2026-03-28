import os
from utils.weatherinfo import WeatherForecastTool
from langchain.tools import tool
from typing import List
from dotenv import load_dotenv

class WeatherInfoTool:
    def __init__(self):
        load_dotenv()
        self.weather_service = WeatherForecastTool()
        self.weather_tool_list = self._setup_tools()
    
    def _setup_tools(self) -> List:
        """Setup all tools for the weather forecast tool"""
        @tool
        def get_current_weather(city: str) -> str:
            """Fetch live weather for one city using Open-Meteo."""
            weather_data = self.weather_service.get_current_weather(city)
            current = weather_data.get('current_weather', {}) if weather_data else {}
            if current:
                temp = current.get('temperature', 'N/A')
                wind = current.get('windspeed', 'N/A')
                code = current.get('weathercode', 'N/A')
                return f"Current weather in {city}: {temp}°C, wind {wind} km/h, weather code {code}"
            return f"Could not fetch weather for {city}"
        
        @tool
        def get_weather_forecast(city: str) -> str:
            """Get weather forecast for a city using Open-Meteo."""
            forecast_data = self.weather_service.get_forecast_weather(city)
            daily = forecast_data.get('daily', {}) if forecast_data else {}
            if daily and daily.get('time'):
                forecast_summary = []
                dates = daily.get('time', [])
                temps_max = daily.get('temperature_2m_max', [])
                temps_min = daily.get('temperature_2m_min', [])
                precip = daily.get('precipitation_sum', [])
                days = min(len(dates), len(temps_max), len(temps_min))
                for i in range(days):
                    date = dates[i]
                    tmax = temps_max[i]
                    tmin = temps_min[i]
                    rain = precip[i] if i < len(precip) else 'N/A'
                    forecast_summary.append(
                        f"{date}: high {tmax}°C, low {tmin}°C, precipitation {rain} mm"
                    )
                return f"Weather forecast for {city}:\n" + "\n".join(forecast_summary)
            return f"Could not fetch forecast for {city}"
    
        return [get_current_weather, get_weather_forecast]