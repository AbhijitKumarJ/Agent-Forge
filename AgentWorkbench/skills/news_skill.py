from core import BaseSkill
try:
    import requests
except ImportError:
    requests = None

class NewsSkill(BaseSkill):
    """A skill that fetches latest headlines for a topic using NewsAPI (demo, requires free API key)."""
    def __init__(self, name, description, api_key=None):
        super().__init__(name, description)
        self.api_key = api_key

    def execute(self, topic, **kwargs):
        if not requests:
            print("[NewsSkill] requests package not installed.")
            return None
        if not self.api_key:
            print("[NewsSkill] No API key provided.")
            return None
        url = f"https://newsapi.org/v2/top-headlines?q={topic}&apiKey={self.api_key}&language=en&pageSize=3"
        try:
            resp = requests.get(url, timeout=5)
            data = resp.json()
            if data.get('status') != 'ok':
                print(f"[NewsSkill] API error: {data.get('message')}")
                return None
            headlines = [a['title'] for a in data.get('articles', [])]
            print(f"[NewsSkill] Headlines: {headlines}")
            return headlines
        except Exception as e:
            print(f"[NewsSkill] Error: {e}")
            return None
