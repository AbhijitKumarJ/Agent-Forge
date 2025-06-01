from core import BaseSkill
try:
    import requests
except ImportError:
    requests = None

class WeatherSkill(BaseSkill):
    """A skill that fetches current weather for a city using Open-Meteo API (no key required)."""
    def execute(self, city, **kwargs):
        if not requests:
            print("[WeatherSkill] requests package not installed.")
            return None
        # Open-Meteo API: https://open-meteo.com/en/docs
        url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}"
        try:
            geo = requests.get(url, timeout=5).json()
            if not geo.get('results'):
                print("[WeatherSkill] City not found.")
                return None
            lat = geo['results'][0]['latitude']
            lon = geo['results'][0]['longitude']
            weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
            weather = requests.get(weather_url, timeout=5).json()
            info = weather.get('current_weather', {})
            print(f"[WeatherSkill] Weather for {city}: {info}")
            return info
        except Exception as e:
            print(f"[WeatherSkill] Error: {e}")
            return None
