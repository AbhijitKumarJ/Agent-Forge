import unittest
from unittest.mock import patch, MagicMock
import os
import openai # For openai.APIError types
from skills import LLMSkill # Assuming correct import

class TestLLMSkill(unittest.TestCase):

    def setUp(self):
        # Store original env var if exists, to restore later
        self.original_openai_api_key = os.environ.get("OPENAI_API_KEY")
        # Set a dummy API key for testing purposes.
        # The actual API calls will be mocked, so the key's value doesn't matter for tests,
        # but __init__ checks for its presence.
        os.environ["OPENAI_API_KEY"] = "dummy_test_key_set_by_setup"
        self.skill = LLMSkill()

    def tearDown(self):
        # Restore original environment variable state
        if self.original_openai_api_key is None:
            # If it was None originally, try to delete it if it was set by setUp
            if os.environ.get("OPENAI_API_KEY") == "dummy_test_key_set_by_setup":
                del os.environ["OPENAI_API_KEY"]
        else:
            # If it had a value, restore it
            os.environ["OPENAI_API_KEY"] = self.original_openai_api_key

    @patch('skills.llm_skill.openai.OpenAI') # Path to OpenAI client in llm_skill.py
    @patch('builtins.print')
    def test_execute_success(self, mock_print, MockOpenAIClient):
        mock_client_instance = MockOpenAIClient.return_value
        mock_chat_completion = MagicMock()
        mock_chat_completion.choices = [MagicMock(message=MagicMock(content="Generated text here."))]
        mock_client_instance.chat.completions.create.return_value = mock_chat_completion

        prompt = "Test prompt"
        expected_text = "Generated text here."

        result = self.skill.execute(prompt)

        self.assertEqual(result, expected_text)
        MockOpenAIClient.assert_called_once_with(api_key="dummy_test_key_set_by_setup")
        mock_client_instance.chat.completions.create.assert_called_once_with(
            model=self.skill.DEFAULT_MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=self.skill.DEFAULT_MAX_TOKENS,
            temperature=self.skill.DEFAULT_TEMPERATURE,
            n=1,
            stop=None
        )
        mock_print.assert_any_call(f"[{self.skill.name}] LLM Response: {expected_text[:100]}...")

    @patch('skills.llm_skill.openai.OpenAI')
    @patch('builtins.print')
    def test_execute_success_custom_params(self, mock_print, MockOpenAIClient):
        mock_client_instance = MockOpenAIClient.return_value
        mock_chat_completion = MagicMock()
        mock_chat_completion.choices = [MagicMock(message=MagicMock(content="Custom params text."))]
        mock_client_instance.chat.completions.create.return_value = mock_chat_completion

        prompt = "Another prompt"
        custom_max_tokens = 50
        custom_temp = 0.5
        expected_text = "Custom params text."

        result = self.skill.execute(prompt, max_tokens=custom_max_tokens, temperature=custom_temp)

        self.assertEqual(result, expected_text)
        mock_client_instance.chat.completions.create.assert_called_once_with(
            model=self.skill.DEFAULT_MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=custom_max_tokens,
            temperature=custom_temp,
            n=1,
            stop=None
        )

    def test_execute_no_api_key(self):
        current_env_val = os.environ.pop("OPENAI_API_KEY", None) # Remove key and store its value

        with patch('builtins.print') as mock_print:
            # Re-initialize skill for it to pick up the missing key
            skill_no_key = LLMSkill()
            result = skill_no_key.execute("Test prompt")

            self.assertIsNone(result)
            # Check for init warning
            mock_print.assert_any_call(f"[{skill_no_key.name}] Warning: Environment variable OPENAI_API_KEY not set. API calls will likely fail.")
            # Check for execute error
            mock_print.assert_any_call(f"[{skill_no_key.name}] Error: API key not configured. Cannot make API call.")

        # Restore the key only if it was present before this test
        if current_env_val is not None:
            os.environ["OPENAI_API_KEY"] = current_env_val


    @patch('skills.llm_skill.openai.OpenAI')
    @patch('builtins.print')
    def test_execute_openai_authentication_error(self, mock_print, MockOpenAIClient):
        mock_client_instance = MockOpenAIClient.return_value
        mock_client_instance.chat.completions.create.side_effect = openai.AuthenticationError("Invalid API key.", response=MagicMock(), body=None)

        result = self.skill.execute("Prompt causing auth error")
        self.assertIsNone(result)
        mock_print.assert_any_call(f"[{self.skill.name}] OpenAI API Authentication Error (check API key): Invalid API key.")

    @patch('skills.llm_skill.openai.OpenAI')
    @patch('builtins.print')
    def test_execute_openai_rate_limit_error(self, mock_print, MockOpenAIClient):
        mock_client_instance = MockOpenAIClient.return_value
        mock_client_instance.chat.completions.create.side_effect = openai.RateLimitError("Rate limit exceeded.", response=MagicMock(), body=None)

        result = self.skill.execute("Prompt causing rate limit")
        self.assertIsNone(result)
        mock_print.assert_any_call(f"[{self.skill.name}] OpenAI API Rate Limit Exceeded: Rate limit exceeded.")

    @patch('skills.llm_skill.openai.OpenAI')
    @patch('builtins.print')
    def test_execute_openai_api_connection_error(self, mock_print, MockOpenAIClient):
        mock_client_instance = MockOpenAIClient.return_value
        mock_client_instance.chat.completions.create.side_effect = openai.APIConnectionError(message="Failed to connect.")

        result = self.skill.execute("Prompt causing connection error")
        self.assertIsNone(result)
        mock_print.assert_any_call(f"[{self.skill.name}] OpenAI API Connection Error: Failed to connect.")

    @patch('skills.llm_skill.openai.OpenAI')
    @patch('builtins.print')
    def test_execute_openai_api_status_error(self, mock_print, MockOpenAIClient):
        mock_client_instance = MockOpenAIClient.return_value
        # Based on openai library, response attribute should be an httpx.Response like object
        mock_httpx_response = MagicMock()
        mock_httpx_response.status_code = 500
        # You might need to set other attributes on mock_httpx_response if the error handler uses them
        mock_client_instance.chat.completions.create.side_effect = openai.APIStatusError("Server error.", response=mock_httpx_response, body=None)

        result = self.skill.execute("Prompt causing API status error")
        self.assertIsNone(result)
        mock_print.assert_any_call(f"[{self.skill.name}] OpenAI API Status Error: Server error.")


    @patch('skills.llm_skill.openai.OpenAI')
    @patch('builtins.print')
    def test_execute_no_choices_in_response(self, mock_print, MockOpenAIClient):
        mock_client_instance = MockOpenAIClient.return_value
        mock_chat_completion = MagicMock()
        mock_chat_completion.choices = [] # Empty choices list
        mock_client_instance.chat.completions.create.return_value = mock_chat_completion

        result = self.skill.execute("Prompt with no choices")
        self.assertIsNone(result)
        mock_print.assert_any_call(f"[{self.skill.name}] Error: No response choices received from LLM.")

if __name__ == "__main__":
    unittest.main()
