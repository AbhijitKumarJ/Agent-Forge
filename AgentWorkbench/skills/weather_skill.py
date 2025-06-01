import os
import requests
from core import BaseSkill

class WeatherSkill(BaseSkill):
    """A skill to fetch current weather conditions using OpenWeatherMap API."""

    API_BASE_URL = "https://api.openweathermap.org/data/2.5/weather"
    DEFAULT_API_KEY_ENV_VAR = "OPENWEATHERMAP_API_KEY"

    def __init__(self, name="WeatherSkill",
                 description="Fetches current weather conditions for a location.",
                 api_key_env_var=None):
        super().__init__(name, description)
        self.api_key_env_var = api_key_env_var if api_key_env_var else self.DEFAULT_API_KEY_ENV_VAR
        self.api_key = os.getenv(self.api_key_env_var)

        if not self.api_key:
            print(f"[{self.name}] Warning: Environment variable {self.api_key_env_var} not set. API calls will likely fail.")

    def execute(self, location: str, action: str = "get_current_weather", units: str = "metric"):
        """
        Executes a weather-related action.

        Args:
            location (str): The location to get weather for (e.g., "London,UK", "New York,US").
            action (str, optional): The action to perform. Defaults to "get_current_weather".
                                    Currently, only "get_current_weather" is implemented.
            units (str, optional): Units for temperature ('metric' for Celsius,
                                   'imperial' for Fahrenheit, 'standard' for Kelvin).
                                   Defaults to "metric".

        Returns:
            dict or None: A dictionary containing weather data if successful, or None if an error occurs.
        """
        if not self.api_key:
            print(f"[{self.name}] Error: API key ({self.api_key_env_var}) not configured. Cannot make API call.")
            return None

        if action.lower() == "get_current_weather":
            return self._get_current_weather(location, units)
        else:
            print(f"[{self.name}] Error: Action '{action}' is not supported. Supported actions: 'get_current_weather'.")
            return None

    def _get_current_weather(self, location: str, units: str):
        """Helper method to fetch current weather for a given location and units."""
        params = {
            "q": location,
            "appid": self.api_key,
            "units": units
        }

        try:
            response = requests.get(self.API_BASE_URL, params=params, timeout=10)
            response.raise_for_status()  # Raises HTTPError for bad responses (4XX or 5XX)
            data = response.json()

            # Check for OpenWeatherMap specific error messages if status is 200 but error in content
            if data.get("cod") != 200 and data.get("message"): # type: ignore
                # API can return 200 but with an error message in JSON body, e.g. for "city not found" if q is bad
                # but sometimes it returns non-200 for that too. This is a safeguard.
                print(f"[{self.name}] API Error for {location}: {data.get('message')}") # type: ignore
                return None

            # Extracting relevant data
            main_weather = data.get("weather", [{}])[0] # weather is a list, take first element

            weather_info = {
                "location": data.get("name", "Unknown location"),
                "temperature": data.get("main", {}).get("temp"),
                "feels_like": data.get("main", {}).get("feels_like"),
                "condition": main_weather.get("main"),
                "description": main_weather.get("description"),
                "humidity": data.get("main", {}).get("humidity"), # percentage
                "pressure": data.get("main", {}).get("pressure"), # hPa
                "wind_speed": data.get("wind", {}).get("speed"), # m/s for metric, miles/hr for imperial
                "clouds_percent": data.get("clouds", {}).get("all"), # percentage
                "visibility_meters": data.get("visibility"), # meters, max 10km
                "sunrise_timestamp": data.get("sys", {}).get("sunrise"), # UTC timestamp
                "sunset_timestamp": data.get("sys", {}).get("sunset")   # UTC timestamp
            }

            # Filter out None values for cleaner output if some fields are optional or missing
            weather_info_filtered = {k: v for k, v in weather_info.items() if v is not None}

            if not weather_info_filtered.get("temperature") and not weather_info_filtered.get("condition"):
                 print(f"[{self.name}] Key weather data (temp/condition) missing in response for {location}.")
                 print(f"[{self.name}] API Response: {data}")
                 return None

            print(f"[{self.name}] Retrieved weather for {weather_info_filtered.get('location')}: {weather_info_filtered.get('temperature')}° ({units}), {weather_info_filtered.get('description')}")
            return weather_info_filtered

        except requests.exceptions.Timeout as e:
            print(f"[{self.name}] Timeout error fetching weather for {location}: {e}")
        except requests.exceptions.HTTPError as e:
            # Attempt to parse error message from OpenWeatherMap if available in JSON
            error_message = str(e)
            if e.response is not None:
                try:
                    error_data = e.response.json()
                    if "message" in error_data:
                        error_message = error_data["message"]
                except ValueError: # JSONDecodeError
                    error_message = e.response.text if e.response.text else str(e)
            print(f"[{self.name}] HTTP error fetching weather for {location}: {error_message}")
        except requests.exceptions.RequestException as e: # Catch-all for other requests errors
            print(f"[{self.name}] Network error fetching weather for {location}: {e}")
        except ValueError as e: # Handles JSON decoding errors if response is not valid JSON
            print(f"[{self.name}] Error decoding JSON response for {location}: {e}")
        except Exception as e:
            print(f"[{self.name}] An unexpected error occurred while fetching weather for {location}: {e}")

        return None

if __name__ == '__main__':
    print("Attempting to use WeatherSkill (requires OPENWEATHERMAP_API_KEY and requests library)...")

    api_key_present = os.getenv("OPENWEATHERMAP_API_KEY")
    if not api_key_present:
        print("Skipping WeatherSkill example: OPENWEATHERMAP_API_KEY environment variable not found.")
    else:
        weather_skill = WeatherSkill()

        location_to_test = "London,UK"
        print(f"\nFetching current weather for '{location_to_test}':")
        weather_data = weather_skill.execute(location=location_to_test, units="metric")
        if weather_data:
            print(f"Result: {weather_data}")
        else:
            print(f"Could not retrieve weather data for {location_to_test}.")

        location_invalid = "NotARealCityNameXYZ"
        print(f"\nFetching current weather for invalid location '{location_invalid}':")
        weather_data_invalid = weather_skill.execute(location=location_invalid)
        if weather_data_invalid:
            print(f"Result for invalid location: {weather_data_invalid}")
        else:
            print(f"Could not retrieve weather data for {location_invalid} (as expected for invalid location).")

        # Test with imperial units
        location_us = "New York,US"
        print(f"\nFetching current weather for '{location_us}' in imperial units:")
        weather_data_imperial = weather_skill.execute(location=location_us, units="imperial")
        if weather_data_imperial:
            print(f"Result: {weather_data_imperial}")
        else:
            print(f"Could not retrieve weather data for {location_us} in imperial units.")
