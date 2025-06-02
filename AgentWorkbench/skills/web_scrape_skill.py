from core import BaseSkill
try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    requests = None
    BeautifulSoup = None

class WebScrapeSkill(BaseSkill):
    """A skill that scrapes the title and first paragraph from a web page."""
    def execute(self, url, **kwargs):
        if not requests or not BeautifulSoup:
            print("[WebScrapeSkill] Required packages not installed.")
            return None
        try:
            resp = requests.get(url, timeout=5)
            soup = BeautifulSoup(resp.text, 'html.parser')
            title = soup.title.string if soup.title else 'No title'
            para = soup.find('p').get_text() if soup.find('p') else 'No paragraph'
            result = {'title': title, 'paragraph': para}
            print(f"[WebScrapeSkill] {result}")
            return result
        except Exception as e:
            print(f"[WebScrapeSkill] Error: {e}")
            return None
