import os
import requests
from core import BaseSkill

class FinanceSkill(BaseSkill):
    """A skill to fetch financial data, starting with stock prices from Alpha Vantage."""

    API_BASE_URL = "https://www.alphavantage.co/query"
    DEFAULT_API_KEY_ENV_VAR = "ALPHA_VANTAGE_API_KEY"

    def __init__(self, name="FinanceSkill",
                 description="Fetches financial data like stock prices.",
                 api_key_env_var=None):
        super().__init__(name, description)
        self.api_key_env_var = api_key_env_var if api_key_env_var else self.DEFAULT_API_KEY_ENV_VAR
        self.api_key = os.getenv(self.api_key_env_var)

        if not self.api_key:
            print(f"[{self.name}] Warning: Environment variable {self.api_key_env_var} not set. API calls will likely fail.")

    def execute(self, symbol: str, action: str = "get_price"):
        """
        Executes a finance-related action.

        Args:
            symbol (str): The stock ticker symbol (e.g., "AAPL").
            action (str, optional): The action to perform. Defaults to "get_price".
                                    Currently, only "get_price" is implemented.

        Returns:
            dict or None: A dictionary containing the data if successful (e.g.,
                          {'symbol': 'AAPL', 'price': '150.25'}),
                          or None if an error occurs.
        """
        if not self.api_key:
            print(f"[{self.name}] Error: API key ({self.api_key_env_var}) not configured. Cannot make API call.")
            return None

        if action.lower() == "get_price":
            return self._get_stock_price(symbol)
        else:
            print(f"[{self.name}] Error: Action '{action}' is not supported. Supported actions: 'get_price'.")
            return None

    def _get_stock_price(self, symbol: str):
        """Helper method to fetch stock price for a given symbol."""
        params = {
            "function": "GLOBAL_QUOTE",
            "symbol": symbol,
            "apikey": self.api_key,
            "datatype": "json"
        }

        try:
            response = requests.get(self.API_BASE_URL, params=params, timeout=10)
            response.raise_for_status()  # Raises HTTPError for bad responses (4XX or 5XX)
            data = response.json()

            if "Global Quote" in data and data["Global Quote"]:
                quote = data["Global Quote"]
                # Key names from Alpha Vantage API for GLOBAL_QUOTE
                price_key = "05. price"
                symbol_key = "01. symbol"

                if price_key in quote and symbol_key in quote:
                    ret_symbol = quote[symbol_key]
                    ret_price = quote[price_key]
                    print(f"[{self.name}] Retrieved price for {ret_symbol}: {ret_price}")
                    return {"symbol": ret_symbol, "price": ret_price}
                else:
                    print(f"[{self.name}] Error: Price or symbol information not found in API response for {symbol}.")
                    print(f"[{self.name}] API Response: {data}") # Log the actual response for debugging
                    return None
            elif "Error Message" in data:
                print(f"[{self.name}] API Error for {symbol}: {data['Error Message']}")
                return None
            elif "Note" in data: # Alpha Vantage sometimes returns rate limit info in "Note"
                print(f"[{self.name}] API Note for {symbol}: {data['Note']}")
                return None
            else:
                print(f"[{self.name}] Error: Unexpected API response structure for {symbol}.")
                print(f"[{self.name}] API Response: {data}") # Log the actual response
                return None

        except requests.exceptions.Timeout as e:
            print(f"[{self.name}] Timeout error fetching data for {symbol}: {e}")
        except requests.exceptions.HTTPError as e:
            print(f"[{self.name}] HTTP error fetching data for {symbol}: {e}. Response: {e.response.text if e.response else 'No response text'}")
        except requests.exceptions.RequestException as e:
            print(f"[{self.name}] Network error fetching data for {symbol}: {e}")
        except ValueError as e: # Handles JSON decoding errors
            print(f"[{self.name}] Error decoding JSON response for {symbol}: {e}")
        except Exception as e:
            print(f"[{self.name}] An unexpected error occurred while fetching price for {symbol}: {e}")

        return None

if __name__ == '__main__':
    # This example will only work if ALPHA_VANTAGE_API_KEY environment variable is set
    # and the requests library is installed.
    print("Attempting to use FinanceSkill (requires ALPHA_VANTAGE_API_KEY and requests library)...")

    api_key_present = os.getenv("ALPHA_VANTAGE_API_KEY")
    if not api_key_present:
        print("Skipping FinanceSkill example: ALPHA_VANTAGE_API_KEY environment variable not found.")
    else:
        finance_skill = FinanceSkill()

        # Test with a valid symbol
        symbol_to_test = "IBM" # Using IBM as it's often available with demo keys if AlphaVantage allows
        print(f"\nFetching price for '{symbol_to_test}':")
        price_data = finance_skill.execute(symbol=symbol_to_test, action="get_price")
        if price_data:
            print(f"Result: {price_data}")
        else:
            print(f"Could not retrieve price data for {symbol_to_test}.")

        # Test with a potentially invalid symbol (or one that might hit limits with demo key)
        invalid_symbol = "NONEXISTENTSTOCKXYZ"
        print(f"\nFetching price for '{invalid_symbol}':")
        price_data_invalid = finance_skill.execute(symbol=invalid_symbol, action="get_price")
        if price_data_invalid:
            print(f"Result for invalid symbol: {price_data_invalid}") # Should ideally be None
        else:
            print(f"Could not retrieve price data for {invalid_symbol} (as expected for invalid/restricted symbol).")

        # Test unsupported action
        print(f"\nAttempting unsupported action for '{symbol_to_test}':")
        unsupported_action_result = finance_skill.execute(symbol=symbol_to_test, action="get_dividends")
        if unsupported_action_result is None:
            print("Unsupported action handled correctly (returned None).")
        else:
            print(f"Unsupported action test failed: {unsupported_action_result}")
