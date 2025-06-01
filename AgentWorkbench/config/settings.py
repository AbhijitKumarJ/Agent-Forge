# Configuration settings for the Agent Workbench

# Example setting
LOG_LEVEL = "INFO"
AGENT_MEMORY_TYPE = "local_file" # or "database", "cloud_storage"
DATA_PATH = "../data/" # Relative path to the data directory

# Default path for the LogSkill's output file
DEFAULT_LOG_FILE = "AgentWorkbench/data/activity.log"

# -----------------------------------------------------------------------------
# API Keys and External Services
# -----------------------------------------------------------------------------
# For skills that require external API access, API keys should generally be
# set as environment variables for security and flexibility.

# Example for LLMSkill (OpenAI):
# To use LLMSkill, set the OPENAI_API_KEY environment variable:
# export OPENAI_API_KEY='your_actual_openai_api_key'
# The skill will pick this up automatically. Do not hardcode keys here.

# Example for FinanceSkill (Alpha Vantage):
# To use FinanceSkill, set the ALPHA_VANTAGE_API_KEY environment variable:
# export ALPHA_VANTAGE_API_KEY='your_actual_alphavantage_api_key'
# The skill will pick this up automatically.

# Example for WeatherSkill (OpenWeatherMap):
# To use WeatherSkill, set the OPENWEATHERMAP_API_KEY environment variable:
# export OPENWEATHERMAP_API_KEY='your_actual_openweathermap_api_key'
# The skill will pick this up automatically.

# Example for NewsSkill (if it were to use NewsAPI.org):
# NEWS_API_KEY = "your_newsapi_key_here" # Or set as ENV variable NEWS_API_KEY
