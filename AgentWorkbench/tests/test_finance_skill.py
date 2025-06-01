import unittest
from unittest.mock import patch, MagicMock
import os
import requests # For requests.exceptions
from skills import FinanceSkill # Assuming correct import

class TestFinanceSkill(unittest.TestCase):

    def setUp(self):
        self.original_api_key = os.environ.get("ALPHA_VANTAGE_API_KEY")
        # Use a specific string to identify keys set by this setUp
        self.dummy_key_for_test = "dummy_finance_key_set_by_setup_for_finance_skill"
        os.environ["ALPHA_VANTAGE_API_KEY"] = self.dummy_key_for_test
        self.skill = FinanceSkill()

    def tearDown(self):
        if self.original_api_key is None:
            # If it was None originally, delete it only if it was set by this setUp
            if os.environ.get("ALPHA_VANTAGE_API_KEY") == self.dummy_key_for_test:
                del os.environ["ALPHA_VANTAGE_API_KEY"]
        else:
            # If it had a value, restore it
            os.environ["ALPHA_VANTAGE_API_KEY"] = self.original_api_key

    @patch('skills.finance_skill.requests.get')
    @patch('builtins.print')
    def test_get_stock_price_success(self, mock_print, mock_requests_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "Global Quote": {
                "01. symbol": "TESTSYM",
                "05. price": "123.45"
            }
        }
        mock_response.raise_for_status = MagicMock()
        mock_requests_get.return_value = mock_response

        symbol = "TESTSYM"
        expected_data = {"symbol": "TESTSYM", "price": "123.45"}

        result = self.skill.execute(symbol=symbol, action="get_price")

        self.assertEqual(result, expected_data)
        mock_requests_get.assert_called_once()
        args, kwargs = mock_requests_get.call_args
        self.assertEqual(args[0], self.skill.API_BASE_URL)
        self.assertEqual(kwargs['params']['function'], "GLOBAL_QUOTE")
        self.assertEqual(kwargs['params']['symbol'], symbol)
        self.assertEqual(kwargs['params']['apikey'], self.dummy_key_for_test)
        mock_print.assert_any_call(f"[{self.skill.name}] Retrieved price for {symbol}: 123.45")

    def test_execute_no_api_key(self):
        # Store current key (dummy from setUp), then remove
        current_key_val = os.environ.pop("ALPHA_VANTAGE_API_KEY", None)

        # Re-initialize skill for it to pick up no key
        skill_no_key = FinanceSkill()

        with patch('builtins.print') as mock_print:
            result = skill_no_key.execute(symbol="ANY", action="get_price")
            self.assertIsNone(result)
            mock_print.assert_any_call(f"[{skill_no_key.name}] Warning: Environment variable {skill_no_key.api_key_env_var} not set. API calls will likely fail.")
            mock_print.assert_any_call(f"[{skill_no_key.name}] Error: API key ({skill_no_key.api_key_env_var}) not configured. Cannot make API call.")

        # Restore the key if it was present before this test method ran
        if current_key_val is not None:
            os.environ["ALPHA_VANTAGE_API_KEY"] = current_key_val


    @patch('skills.finance_skill.requests.get')
    @patch('builtins.print')
    def test_get_stock_price_api_error_message(self, mock_print, mock_requests_get):
        mock_response = MagicMock()
        mock_response.status_code = 200 # API might return 200 but with an error message in JSON
        mock_response.json.return_value = {"Error Message": "Invalid API call or symbol."}
        mock_response.raise_for_status = MagicMock()
        mock_requests_get.return_value = mock_response

        result = self.skill.execute(symbol="BADSYM", action="get_price")

        self.assertIsNone(result)
        mock_print.assert_any_call(f"[{self.skill.name}] API Error for BADSYM: Invalid API call or symbol.")

    @patch('skills.finance_skill.requests.get')
    @patch('builtins.print')
    def test_get_stock_price_api_note_rate_limit(self, mock_print, mock_requests_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"Note": "API call frequency is 5 calls per minute and 100 calls per day."}
        mock_response.raise_for_status = MagicMock()
        mock_requests_get.return_value = mock_response

        result = self.skill.execute(symbol="TESTSYM", action="get_price")
        self.assertIsNone(result)
        mock_print.assert_any_call(f"[{self.skill.name}] API Note for TESTSYM: API call frequency is 5 calls per minute and 100 calls per day.")


    @patch('skills.finance_skill.requests.get', side_effect=requests.exceptions.Timeout("API request timed out."))
    @patch('builtins.print')
    def test_get_stock_price_timeout_error(self, mock_print, mock_requests_get_timeout):
        result = self.skill.execute(symbol="TIMEOUTSYM", action="get_price")
        self.assertIsNone(result)
        mock_print.assert_any_call(f"[{self.skill.name}] Timeout error fetching data for TIMEOUTSYM: API request timed out.")

    @patch('skills.finance_skill.requests.get')
    @patch('builtins.print')
    def test_get_stock_price_http_error(self, mock_print, mock_requests_get):
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("500 Server Error", response=mock_response)
        mock_requests_get.return_value = mock_response

        result = self.skill.execute(symbol="HTTPERR", action="get_price")
        self.assertIsNone(result)
        mock_print.assert_any_call(f"[{self.skill.name}] HTTP error fetching data for HTTPERR: 500 Server Error. Response: Internal Server Error")

    @patch('skills.finance_skill.requests.get')
    @patch('builtins.print')
    def test_get_stock_price_missing_keys_in_response(self, mock_print, mock_requests_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"Global Quote": {"01. symbol": "TESTSYM"}} # Missing "05. price"
        mock_response.raise_for_status = MagicMock()
        mock_requests_get.return_value = mock_response

        result = self.skill.execute(symbol="TESTSYM", action="get_price")
        self.assertIsNone(result)
        mock_print.assert_any_call(f"[{self.skill.name}] Error: Price or symbol information not found in API response for TESTSYM.")

    @patch('skills.finance_skill.requests.get')
    @patch('builtins.print')
    def test_get_stock_price_unexpected_response_structure(self, mock_print, mock_requests_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"UnexpectedStructure": "data"}
        mock_response.raise_for_status = MagicMock()
        mock_requests_get.return_value = mock_response

        result = self.skill.execute(symbol="TESTSYM", action="get_price")
        self.assertIsNone(result)
        mock_print.assert_any_call(f"[{self.skill.name}] Error: Unexpected API response structure for TESTSYM.")

    @patch('builtins.print')
    def test_execute_unsupported_action(self, mock_print):
        result = self.skill.execute(symbol="TESTSYM", action="get_historical_data")
        self.assertIsNone(result)
        mock_print.assert_any_call(f"[{self.skill.name}] Error: Action 'get_historical_data' is not supported. Supported actions: 'get_price'.")


if __name__ == "__main__":
    unittest.main()
