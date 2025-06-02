import os
import openai # openai library
from core import BaseSkill

class LLMSkill(BaseSkill):
    """A skill to interact with a Large Language Model (OpenAI's GPT)."""

    DEFAULT_MODEL = "gpt-3.5-turbo"
    DEFAULT_MAX_TOKENS = 150
    DEFAULT_TEMPERATURE = 0.7

    def __init__(self, name="LLMSkill", description="Interacts with an OpenAI LLM for text generation.",
                 api_key_env_var="OPENAI_API_KEY", model=None):
        super().__init__(name, description)

        # API key is typically set globally for the openai library via environment variable
        # or openai.api_key = "YOUR_KEY". We'll rely on the environment variable.
        self.api_key = os.getenv(api_key_env_var)
        if not self.api_key:
            print(f"[{self.name}] Warning: Environment variable {api_key_env_var} not set. API calls will likely fail.")
            # The openai library will raise an error if the key is missing when a call is made.

        # Forcing the library to use the key from env var if it was set,
        # though it should pick it up automatically.
        # openai.api_key = self.api_key # This line might be redundant if env var is standard

        self.model = model if model else self.DEFAULT_MODEL

    def execute(self, prompt: str, max_tokens: int = None, temperature: float = None):
        """
        Generates text using the configured LLM.

        Args:
            prompt (str): The prompt to send to the LLM.
            max_tokens (int, optional): Max tokens for the response. Defaults to skill's default.
            temperature (float, optional): Sampling temperature. Defaults to skill's default.

        Returns:
            str: The LLM's generated text, or None if an error occurs.
        """
        if not self.api_key:
            print(f"[{self.name}] Error: API key not configured. Cannot make API call.")
            return None

        current_max_tokens = max_tokens if max_tokens is not None else self.DEFAULT_MAX_TOKENS
        current_temperature = temperature if temperature is not None else self.DEFAULT_TEMPERATURE

        try:
            # Using ChatCompletion endpoint
            # Note: Ensure you have the latest openai library version (e.g., pip install --upgrade openai)
            # For older versions, the API structure might be different.
            # This example assumes a newer version (e.g., 1.x.x)

            # The openai library now uses a client instance
            client = openai.OpenAI(api_key=self.api_key) # Initialize client with key

            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                max_tokens=current_max_tokens,
                temperature=current_temperature,
                n=1, # Number of completions to generate
                stop=None # Optional stop sequences
            )

            # Extracting the text from the response
            # The structure is response.choices[0].message.content
            if response.choices and len(response.choices) > 0:
                generated_text = response.choices[0].message.content.strip()
                print(f"[{self.name}] LLM Response: {generated_text[:100]}...") # Print a snippet
                return generated_text
            else:
                print(f"[{self.name}] Error: No response choices received from LLM.")
                return None

        except openai.APIConnectionError as e:
            print(f"[{self.name}] OpenAI API Connection Error: {e}")
        except openai.RateLimitError as e:
            print(f"[{self.name}] OpenAI API Rate Limit Exceeded: {e}")
        except openai.AuthenticationError as e:
            print(f"[{self.name}] OpenAI API Authentication Error (check API key): {e}")
        except openai.APIStatusError as e: # General API error
            print(f"[{self.name}] OpenAI API Status Error: {e}")
        except Exception as e:
            print(f"[{self.name}] An unexpected error occurred: {e}")

        return None

if __name__ == '__main__':
    # This example will only work if OPENAI_API_KEY environment variable is set
    # and the openai library is installed.
    print("Attempting to use LLMSkill (requires OPENAI_API_KEY and openai library)...")

    # Check if API key is available for the example
    if not os.getenv("OPENAI_API_KEY"):
        print("Skipping LLMSkill example: OPENAI_API_KEY environment variable not found.")
    else:
        try:
            llm_skill = LLMSkill()
            example_prompt = "Translate the following English text to French: 'Hello, world!'"
            print(f"Sending prompt: '{example_prompt}'")

            response_text = llm_skill.execute(example_prompt, max_tokens=50)

            if response_text:
                print(f"LLM Full Response:\n{response_text}")
            else:
                print("LLM Skill execution failed or returned no text.")

            example_prompt_2 = "What is the capital of France?"
            print(f"\nSending prompt: '{example_prompt_2}'")
            response_text_2 = llm_skill.execute(example_prompt_2, max_tokens=30, temperature=0.5)
            if response_text_2:
                print(f"LLM Full Response:\n{response_text_2}")
            else:
                print("LLM Skill execution failed or returned no text for prompt 2.")

        except ImportError:
            print("OpenAI library not installed. Skipping LLMSkill example.")
        except Exception as e:
            print(f"An error occurred during the LLMSkill example: {e}")
