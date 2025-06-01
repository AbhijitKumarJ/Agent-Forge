import unittest
from unittest.mock import patch, MagicMock
import requests # For requests.exceptions.RequestException
import xml.etree.ElementTree as ET # For ET.ParseError
from skills import NewsSkill # Assuming correct import

# Sample RSS feed content (simplified)
SAMPLE_RSS_VALID = """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
<channel>
    <title>BBC News</title>
    <item>
        <title>Headline 1: The Quick Brown Fox</title>
        <link>http://example.com/1</link>
        <description>Description 1</description>
    </item>
    <item>
        <title>Headline 2: Jumps Over The Lazy Dog</title>
        <link>http://example.com/2</link>
        <description>Description 2</description>
    </item>
    <item>
        <title>Headline 3: And Other News</title>
        <link>http://example.com/3</link>
        <description>Description 3</description>
    </item>
</channel>
</rss>"""

SAMPLE_RSS_VALID_NO_CHANNEL = """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
    <item>
        <title>Headline A: Direct Item</title>
        <link>http://example.com/A</link>
    </item>
    <item>
        <title>Headline B: Another Direct Item</title>
        <link>http://example.com/B</link>
    </item>
</rss>"""


SAMPLE_RSS_EMPTY = """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
<channel>
    <title>Empty News</title>
</channel>
</rss>"""

SAMPLE_RSS_MALFORMED = """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
<channel>
    <title>Malformed News</title>
    <item>
        <title>Only item, but channel not closed properly
</channel>
</rss>"""


class TestNewsSkill(unittest.TestCase):

    def setUp(self):
        self.skill = NewsSkill() # Uses default BBC RSS, but will be mocked

    @patch('skills.news_skill.requests.get')
    @patch('builtins.print') # To suppress and optionally check print statements
    def test_execute_success_default_count(self, mock_print, mock_requests_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = SAMPLE_RSS_VALID.encode('utf-8')
        mock_response.raise_for_status = MagicMock() # Ensure it doesn't raise
        mock_requests_get.return_value = mock_response

        headlines = self.skill.execute() # Default count is 5

        self.assertEqual(len(headlines), 3) # Sample has 3 items
        self.assertEqual(headlines[0], "Headline 1: The Quick Brown Fox")
        self.assertEqual(headlines[1], "Headline 2: Jumps Over The Lazy Dog")
        self.assertEqual(headlines[2], "Headline 3: And Other News")
        mock_requests_get.assert_called_once_with(self.skill.DEFAULT_RSS_URL, timeout=10)
        mock_print.assert_any_call(f"[{self.skill.name}] Retrieved 3 headlines from {self.skill.DEFAULT_RSS_URL}")

    @patch('skills.news_skill.requests.get')
    @patch('builtins.print')
    def test_execute_success_custom_count(self, mock_print, mock_requests_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = SAMPLE_RSS_VALID.encode('utf-8')
        mock_response.raise_for_status = MagicMock()
        mock_requests_get.return_value = mock_response

        headlines = self.skill.execute(count=2)

        self.assertEqual(len(headlines), 2)
        self.assertEqual(headlines[0], "Headline 1: The Quick Brown Fox")
        self.assertEqual(headlines[1], "Headline 2: Jumps Over The Lazy Dog")

    @patch('skills.news_skill.requests.get')
    @patch('builtins.print')
    def test_execute_success_fallback_no_channel(self, mock_print, mock_requests_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = SAMPLE_RSS_VALID_NO_CHANNEL.encode('utf-8')
        mock_response.raise_for_status = MagicMock()
        mock_requests_get.return_value = mock_response

        headlines = self.skill.execute(count=2)
        self.assertEqual(len(headlines), 2)
        self.assertEqual(headlines[0], "Headline A: Direct Item")
        self.assertEqual(headlines[1], "Headline B: Another Direct Item")
        mock_print.assert_any_call(f"[{self.skill.name}] Retrieved 2 headlines from {self.skill.DEFAULT_RSS_URL}")


    @patch('skills.news_skill.requests.get')
    @patch('builtins.print')
    def test_execute_http_error(self, mock_print, mock_requests_get):
        mock_response = MagicMock()
        mock_response.status_code = 404
        # Configure raise_for_status to actually raise an error
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("404 Client Error")
        mock_requests_get.return_value = mock_response

        headlines = self.skill.execute()

        self.assertEqual(headlines, [])
        mock_print.assert_any_call(f"[{self.skill.name}] Error fetching news from {self.skill.DEFAULT_RSS_URL}: 404 Client Error")

    @patch('skills.news_skill.requests.get', side_effect=requests.exceptions.Timeout("Timeout occurred"))
    @patch('builtins.print')
    def test_execute_request_timeout(self, mock_print, mock_requests_get_timeout):
        headlines = self.skill.execute()

        self.assertEqual(headlines, [])
        mock_print.assert_any_call(f"[{self.skill.name}] Error fetching news from {self.skill.DEFAULT_RSS_URL}: Timeout occurred")

    @patch('skills.news_skill.requests.get')
    @patch('builtins.print')
    def test_execute_parsing_error(self, mock_print, mock_requests_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = SAMPLE_RSS_MALFORMED.encode('utf-8') # Malformed XML
        mock_response.raise_for_status = MagicMock()
        mock_requests_get.return_value = mock_response

        headlines = self.skill.execute()

        self.assertEqual(headlines, [])
        # The exact error message from ET.ParseError can be verbose and platform-dependent.
        # Checking that *a* parse error message was printed is usually sufficient.
        self.assertTrue(any("Error parsing XML" in call_args[0][0] for call_args in mock_print.call_args_list))


    @patch('skills.news_skill.requests.get')
    @patch('builtins.print')
    def test_execute_empty_feed(self, mock_print, mock_requests_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = SAMPLE_RSS_EMPTY.encode('utf-8')
        mock_response.raise_for_status = MagicMock()
        mock_requests_get.return_value = mock_response

        headlines = self.skill.execute()

        self.assertEqual(headlines, [])
        mock_print.assert_any_call(f"[{self.skill.name}] No headlines found or failed to parse items correctly from {self.skill.DEFAULT_RSS_URL}")

    @patch('skills.news_skill.requests.get')
    @patch('builtins.print')
    def test_execute_count_exceeds_available_items(self, mock_print, mock_requests_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = SAMPLE_RSS_VALID.encode('utf-8') # Contains 3 items
        mock_response.raise_for_status = MagicMock()
        mock_requests_get.return_value = mock_response

        headlines = self.skill.execute(count=10) # Request 10, but only 3 available

        self.assertEqual(len(headlines), 3) # Should return all 3 available items


if __name__ == "__main__":
    unittest.main()
