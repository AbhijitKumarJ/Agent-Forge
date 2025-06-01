from core import BaseSkill
import os
try:
    import openai
except ImportError:
    openai = None

class LLMCompletionSkill(BaseSkill):
    """A skill that calls the OpenAI API for completion."""
    def __init__(self, name, description, model="gpt-3.5-turbo"):
        super().__init__(name, description)
        self.model = model
        self.api_key = os.environ.get("OPENAI_API_KEY")

    def execute(self, prompt, **kwargs):
        if not openai:
            print("[LLMCompletionSkill] OpenAI Python package not installed.")
            return None
        if not self.api_key:
            print("[LLMCompletionSkill] OPENAI_API_KEY not set.")
            return None
        try:
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=100
            )
            result = response.choices[0].message["content"].strip()
            print(f"[LLMCompletionSkill] Response: {result}")
            return result
        except Exception as e:
            print(f"[LLMCompletionSkill] Error: {e}")
            return None
