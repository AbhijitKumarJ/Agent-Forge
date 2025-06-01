from core import BaseSkill
try:
    import requests
except ImportError:
    requests = None

class FinanceSkill(BaseSkill):
    """A skill that fetches current stock price for a symbol using Yahoo Finance API (public endpoint)."""
    def execute(self, symbol, **kwargs):
        if not requests:
            print("[FinanceSkill] requests package not installed.")
            return None
        url = f"https://query1.finance.yahoo.com/v7/finance/quote?symbols={symbol}"
        try:
            resp = requests.get(url, timeout=5)
            data = resp.json()
            quote = data['quoteResponse']['result']
            if not quote:
                print(f"[FinanceSkill] Symbol {symbol} not found.")
                return None
            price = quote[0].get('regularMarketPrice')
            print(f"[FinanceSkill] {symbol} price: {price}")
            return price
        except Exception as e:
            print(f"[FinanceSkill] Error: {e}")
            return None
