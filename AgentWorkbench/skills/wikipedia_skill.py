from core import BaseSkill
try:
    import requests
except ImportError:
    requests = None

class WikipediaSkill(BaseSkill):
    """A skill that fetches a Wikipedia summary for a given topic using Wikipedia REST API."""
    def execute(self, topic, **kwargs):
        if not requests:
            print("[WikipediaSkill] requests package not installed.")
            return None
        url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{topic.replace(' ', '_')}"
        try:
            resp = requests.get(url, timeout=5)
            if resp.status_code != 200:
                print(f"[WikipediaSkill] Topic '{topic}' not found.")
                return None
            data = resp.json()
            summary = data.get('extract', 'No summary found.')
            print(f"[WikipediaSkill] {topic}: {summary}")
            return summary
        except Exception as e:
            print(f"[WikipediaSkill] Error: {e}")
            return None
