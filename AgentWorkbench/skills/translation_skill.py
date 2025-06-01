from core import BaseSkill
try:
    import requests
except ImportError:
    requests = None

class TranslationSkill(BaseSkill):
    """A skill that translates text using LibreTranslate public API (no key required for demo usage)."""
    def execute(self, text, target_lang="es", **kwargs):
        if not requests:
            print("[TranslationSkill] requests package not installed.")
            return None
        url = "https://libretranslate.com/translate"
        data = {
            "q": text,
            "source": "auto",
            "target": target_lang,
            "format": "text"
        }
        try:
            resp = requests.post(url, data=data, timeout=5)
            result = resp.json()
            translated = result.get("translatedText", "Translation failed.")
            print(f"[TranslationSkill] {text} -> {translated}")
            return translated
        except Exception as e:
            print(f"[TranslationSkill] Error: {e}")
            return None
