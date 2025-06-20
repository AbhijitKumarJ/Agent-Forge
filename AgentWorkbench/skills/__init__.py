# Skills package
from .echo_skill import EchoSkill
from .math_skill import MathSkill
from .log_skill import LogSkill
from .llm_skill import LLMSkill # Changed from LLMCompletionSkill
from .web_search_skill import WebSearchSkill
from .web_scrape_skill import WebScrapeSkill
from .weather_skill import WeatherSkill
from .finance_skill import FinanceSkill
from .news_skill import NewsSkill
from .wikipedia_skill import WikipediaSkill
from .translation_skill import TranslationSkill

__all__ = [
    "EchoSkill",
    "MathSkill",
    "LogSkill",
    "LLMSkill", # Changed from LLMCompletionSkill
    "WebSearchSkill",
    "WebScrapeSkill",
    "WeatherSkill",
    "FinanceSkill",
    "NewsSkill",
    "WikipediaSkill",
    "TranslationSkill",
]