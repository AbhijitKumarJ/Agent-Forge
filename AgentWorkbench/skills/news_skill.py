import requests
import xml.etree.ElementTree as ET
from core import BaseSkill

class NewsSkill(BaseSkill):
    """A skill to fetch top news headlines from an RSS feed."""

    # Default RSS feed URL (BBC News Front Page)
    DEFAULT_RSS_URL = "http://feeds.bbci.co.uk/news/rss.xml"

    def __init__(self, name="NewsSkill", description="Fetches top news headlines.", rss_url=None):
        super().__init__(name, description)
        self.rss_url = rss_url if rss_url else self.DEFAULT_RSS_URL

    def execute(self, category: str = "news", count: int = 5):
        """
        Fetches top news headlines.

        Args:
            category (str, optional): The news category (currently ignored, uses default feed).
                                      Defaults to "news".
            count (int, optional): The maximum number of headlines to return.
                                   Defaults to 5.

        Returns:
            list: A list of headline strings, or an empty list if an error occurs.
        """
        headlines = []
        try:
            # In a real scenario, you might want to use a session with headers
            response = requests.get(self.rss_url, timeout=10) # Added timeout
            response.raise_for_status()  # Raises an HTTPError for bad responses (4XX or 5XX)

            root = ET.fromstring(response.content)

            # RSS feeds typically have items under channel -> item
            # Some feeds might have items directly under the root if it's a simpler structure,
            # but standard RSS has a channel.
            items_found = 0
            for item in root.findall('./channel/item'):
                if items_found >= count:
                    break
                title_element = item.find('title')
                if title_element is not None and title_element.text:
                    headlines.append(title_element.text)
                    items_found += 1

            if not headlines and items_found == 0: # Check if any items were processed
                 # Fallback if ./channel/item finds nothing, try finding items directly under root
                 # This is less common for standard RSS but can be a fallback.
                for item in root.findall('item'): # Check for items directly under root
                    if items_found >= count:
                        break
                    title_element = item.find('title')
                    if title_element is not None and title_element.text:
                        headlines.append(title_element.text)
                        items_found += 1

            if items_found > 0:
                print(f"[{self.name}] Retrieved {len(headlines)} headlines from {self.rss_url}")
            else:
                print(f"[{self.name}] No headlines found or failed to parse items correctly from {self.rss_url}")


        except requests.exceptions.RequestException as e:
            print(f"[{self.name}] Error fetching news from {self.rss_url}: {e}")
        except ET.ParseError as e:
            print(f"[{self.name}] Error parsing XML from {self.rss_url}: {e}")
        except Exception as e:
            print(f"[{self.name}] An unexpected error occurred: {e}")

        return headlines

if __name__ == '__main__':
    # Example Usage (for direct testing of the skill file)
    news_skill = NewsSkill()

    print("Fetching default headlines (BBC News):")
    bbc_headlines = news_skill.execute(count=3)
    if bbc_headlines:
        for i, headline in enumerate(bbc_headlines):
            print(f"{i+1}. {headline}")
    else:
        print("No headlines retrieved or an error occurred.")

    # Example with a (potentially different) RSS feed if you want to test flexibility
    # For this to work, you'd need another valid RSS feed URL.
    # alt_rss_url = "https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml" # Example
    # custom_news_skill = NewsSkill(rss_url=alt_rss_url)
    # print(f"\nFetching headlines from {alt_rss_url}:")
    # custom_headlines = custom_news_skill.execute(count=2)
    # if custom_headlines:
    #     for i, headline in enumerate(custom_headlines):
    #         print(f"{i+1}. {headline}")
    # else:
    #     print("No headlines retrieved or an error occurred.")
