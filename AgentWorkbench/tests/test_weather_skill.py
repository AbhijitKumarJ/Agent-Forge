import unittest
from unittest.mock import patch, MagicMock
import os
import requests # For requests.exceptions
from skills import WeatherSkill # Assuming correct import

# Sample OpenWeatherMap API response for current weather
SAMPLE_WEATHER_DATA_METRIC = {
    "coord": {"lon": -0.1257, "lat": 51.5085},
    "weather": [{"id": 803, "main": "Clouds", "description": "broken clouds", "icon": "04d"}],
    "base": "stations",
    "main": {
        "temp": 15.0, # Celsius for metric
        "feels_like": 14.5,
        "temp_min": 13.0,
        "temp_max": 16.5,
        "pressure": 1012,
        "humidity": 80
    },
    "visibility": 10000,
    "wind": {"speed": 5.1, "deg": 240}, # m/s for metric
    "clouds": {"all": 75},
    "dt": 1678886400,
    "sys": {"type": 1, "id": 1414, "country": "GB", "sunrise": 1678857600, "sunset": 1678899600},
    "timezone": 0,
    "id": 2643743,
    "name": "London",
    "cod": 200
}

SAMPLE_WEATHER_DATA_IMPERIAL = {
    "coord": {"lon": -74.006, "lat": 40.7128},
    "weather": [{"id": 800, "main": "Clear", "description": "clear sky", "icon": "01d"}],
    "base": "stations",
    "main": {
        "temp": 68.0, # Fahrenheit for imperial
        "feels_like": 67.0,
        "temp_min": 65.0,
        "temp_max": 70.0,
        "pressure": 1015,
        "humidity": 60
    },
    "visibility": 10000, # Still meters by default from API, though skill doesn't convert this
    "wind": {"speed": 10.0, "deg": 180}, # miles/hour for imperial
    "clouds": {"all": 0},
    "dt": 1678886400,
    "sys": {"type": 1, "id": 2004109, "country": "US", "sunrise": 1678878000, "sunset": 1678918800},
    "timezone": -14400,
    "id": 5128581,
    "name": "New York",
    "cod": 200
}


class TestWeatherSkill(unittest.TestCase):

    def setUp(self):
        self.original_api_key = os.environ.get("OPENWEATHERMAP_API_KEY")
        self.dummy_key_for_test = "dummy_weather_key_set_by_setup_for_weather_skill" # Make key specific
        os.environ["OPENWEATHERMAP_API_KEY"] = self.dummy_key_for_test
        self.skill = WeatherSkill()

    def tearDown(self):
        if self.original_api_key is None:
            # If it was None originally, delete it only if it was set by this setUp
            if os.environ.get("OPENWEATHERMAP_API_KEY") == self.dummy_key_for_test:
                del os.environ["OPENWEATHERMAP_API_KEY"]
        else:
            # If it had a value, restore it
            os.environ["OPENWEATHERMAP_API_KEY"] = self.original_api_key

    @patch('skills.weather_skill.requests.get')
    @patch('builtins.print')
    def test_get_current_weather_success_metric(self, mock_print, mock_requests_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = SAMPLE_WEATHER_DATA_METRIC
        mock_response.raise_for_status = MagicMock()
        mock_requests_get.return_value = mock_response

        location = "London,UK"
        units = "metric"
        result = self.skill.execute(location=location, action="get_current_weather", units=units)

        self.assertIsNotNone(result)
        self.assertEqual(result.get("location"), "London")
        self.assertEqual(result.get("temperature"), 15.0)
        self.assertEqual(result.get("condition"), "Clouds")
        self.assertEqual(result.get("description"), "broken clouds")
        self.assertEqual(result.get("humidity"), 80)
        self.assertEqual(result.get("wind_speed"), 5.1)

        mock_requests_get.assert_called_once()
        args, kwargs = mock_requests_get.call_args
        self.assertEqual(args[0], self.skill.API_BASE_URL)
        self.assertEqual(kwargs['params']['q'], location)
        self.assertEqual(kwargs['params']['appid'], self.dummy_key_for_test)
        self.assertEqual(kwargs['params']['units'], units)
        mock_print.assert_any_call(f"[{self.skill.name}] Retrieved weather for London: 15.0° ({units}), broken clouds")

    @patch('skills.weather_skill.requests.get')
    @patch('builtins.print')
    def test_get_current_weather_success_imperial(self, mock_print, mock_requests_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = SAMPLE_WEATHER_DATA_IMPERIAL
        mock_response.raise_for_status = MagicMock()
        mock_requests_get.return_value = mock_response

        location = "New York,US"
        units = "imperial"
        result = self.skill.execute(location=location, units=units) # action defaults to get_current_weather

        self.assertIsNotNone(result)
        self.assertEqual(result.get("location"), "New York")
        self.assertEqual(result.get("temperature"), 68.0) # Fahrenheit
        self.assertEqual(result.get("condition"), "Clear")
        self.assertEqual(result.get("wind_speed"), 10.0) # mph
        mock_print.assert_any_call(f"[{self.skill.name}] Retrieved weather for New York: 68.0° ({units}), clear sky")


    def test_execute_no_api_key(self):
        current_key_val = os.environ.pop("OPENWEATHERMAP_API_KEY", None)
        skill_no_key = WeatherSkill() # Re-initialize

        with patch('builtins.print') as mock_print:
            result = skill_no_key.execute(location="ANY")
            self.assertIsNone(result)
            mock_print.assert_any_call(f"[{skill_no_key.name}] Warning: Environment variable {skill_no_key.api_key_env_var} not set. API calls will likely fail.")
            mock_print.assert_any_call(f"[{skill_no_key.name}] Error: API key ({skill_no_key.api_key_env_var}) not configured. Cannot make API call.")

        if current_key_val is not None:
            os.environ["OPENWEATHERMAP_API_KEY"] = current_key_val

    @patch('skills.weather_skill.requests.get')
    @patch('builtins.print')
    def test_get_current_weather_api_error_message_in_json(self, mock_print, mock_requests_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"cod": "404", "message": "city not found"} # OpenWeatherMap uses string "404" for cod
        mock_response.raise_for_status = MagicMock()
        mock_requests_get.return_value = mock_response

        result = self.skill.execute(location="InvalidCity", action="get_current_weather")

        self.assertIsNone(result)
        mock_print.assert_any_call(f"[{self.skill.name}] API Error for InvalidCity: city not found")


    @patch('skills.weather_skill.requests.get')
    @patch('builtins.print')
    def test_get_current_weather_http_error_401_unauthorized(self, mock_print, mock_requests_get):
        mock_response = MagicMock(spec=requests.Response)
        mock_response.status_code = 401
        mock_response.json.return_value = {"cod": 401, "message": "Invalid API key."} # OWM returns int 401 for cod
        mock_response.text = mock_response.json.return_value["message"]
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("401 Client Error: Unauthorized", response=mock_response)
        mock_requests_get.return_value = mock_response

        result = self.skill.execute(location="AnyCity", action="get_current_weather")
        self.assertIsNone(result)
        mock_print.assert_any_call(f"[{self.skill.name}] HTTP error fetching weather for AnyCity: Invalid API key.")


    @patch('skills.weather_skill.requests.get', side_effect=requests.exceptions.Timeout("API request timed out."))
    @patch('builtins.print')
    def test_get_current_weather_timeout_error(self, mock_print, mock_requests_get_timeout):
        result = self.skill.execute(location="TimeoutCity", action="get_current_weather")
        self.assertIsNone(result)
        mock_print.assert_any_call(f"[{self.skill.name}] Timeout error fetching weather for TimeoutCity: API request timed out.")

    @patch('skills.weather_skill.requests.get')
    @patch('builtins.print')
    def test_get_current_weather_missing_main_keys_in_response(self, mock_print, mock_requests_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"coord": {}, "name": "PartialCity", "cod": 200, "weather": [{}]}
        mock_response.raise_for_status = MagicMock()
        mock_requests_get.return_value = mock_response

        result = self.skill.execute(location="PartialCity", action="get_current_weather")
        self.assertIsNone(result)
        mock_print.assert_any_call(f"[{self.skill.name}] Key weather data (temp/condition) missing in response for PartialCity.")

    @patch('builtins.print')
    def test_execute_unsupported_action(self, mock_print):
        result = self.skill.execute(location="Anywhere", action="get_7_day_forecast")
        self.assertIsNone(result)
        mock_print.assert_any_call(f"[{self.skill.name}] Error: Action 'get_7_day_forecast' is not supported. Supported actions: 'get_current_weather'.")

if __name__ == "__main__":
    unittest.main()
