from core import BaseSkill
try:
    import requests
except ImportError:
    requests = None

class WebSearchSkill(BaseSkill):
    """A skill that performs a simple web search using DuckDuckGo Instant Answer API."""
    def execute(self, query, **kwargs):
        if not requests:
            print("[WebSearchSkill] requests package not installed.")
            return None
        url = f"https://api.duckduckgo.com/?q={query}&format=json"
        try:
            resp = requests.get(url, timeout=5)
            data = resp.json()
            answer = data.get('AbstractText') or data.get('Answer') or 'No answer found.'
            print(f"[WebSearchSkill] Answer: {answer}")
            return answer
        except Exception as e:
            print(f"[WebSearchSkill] Error: {e}")
            return None
