# AgentWorkbench: Skill & Tool Maturity Plan - Phase 1

## 1. Rationale and Goals
Many skills and tools within AgentWorkbench were initially created as placeholders or with very basic functionality to establish the framework. The "Skill & Tool Maturity" initiative aims to incrementally enhance these components, making them more robust, functional, and closer to real-world usability.

**Core Goals for this Initiative:**
- **Enhance Functionality:** Implement or expand the core logic of placeholder skills/tools.
- **Improve Error Handling:** Make components more resilient to unexpected inputs or external issues.
- **Integrate with External Services:** Where appropriate, connect skills to live APIs or data sources (while ensuring testability through mocking).
- **Increase Configurability:** Allow key parameters to be set via the `config/settings.py` file or at runtime.
- **Add Comprehensive Testing:** Ensure all matured components have thorough unit tests.

This document will track the progress of this initiative, starting with `NewsSkill`.

## 2. Phase 1 Implementation: `NewsSkill` Enhancement (Completed)

### a. Initial State
The `NewsSkill` was initially a placeholder without actual data fetching capabilities.

### b. Enhancements Made
- **Data Source:** Integrated with the live BBC News RSS feed (`http://feeds.bbci.co.uk/news/rss.xml`) as a default source. The RSS URL can also be customized when instantiating the skill.
- **Functionality:**
    - Fetches news headlines using the `requests` library.
    - Parses the XML content of the RSS feed using `xml.etree.ElementTree`.
    - Extracts a specified number of headlines (defaulting to 5).
    - Includes a fallback mechanism to parse items directly under the RSS root if the standard `channel/item` path yields no results.
    - Returns a list of headline strings.
- **Error Handling:**
    - Handles potential network errors during fetching (e.g., `requests.exceptions.RequestException`, HTTP errors via `response.raise_for_status()`).
    - Handles XML parsing errors (`ET.ParseError`).
    - Returns an empty list `[]` in case of errors, with error messages printed to the console.
- **Unit Tests:**
    - Comprehensive unit tests were added in `AgentWorkbench/tests/test_news_skill.py`.
    - Tests use `unittest.mock` to simulate `requests.get` calls, providing mock RSS data (valid, empty, malformed).
    - Coverage includes successful headline retrieval, HTTP errors, request timeouts, parsing errors, and handling of empty feeds.

## 3. Future Candidates for Skill/Tool Maturity

The following skills and tools are key candidates for future enhancement efforts:

### Skills:
- **`FinanceSkill` (Phase 2 - Initial Implementation Completed):**
    - **Current State:** Basic stock price fetching functionality implemented.
    - **Functionality Added:**
        - Integrates with the Alpha Vantage API (specifically the `GLOBAL_QUOTE` function) to fetch the latest stock price for a given symbol.
        - The `execute` method takes a `symbol` (string) and an `action` (string, defaults to "get_price"). Currently, only "get_price" is implemented.
        - Returns a dictionary `{"symbol": "ACTUAL_SYMBOL", "price": "PRICE_AS_STRING"}` on success, or `None` on failure.
    - **API Key Management:**
        - Expects the Alpha Vantage API key to be set as an environment variable `ALPHA_VANTAGE_API_KEY`.
        - The skill checks for this variable and provides a warning if not set; API calls will fail without it.
        - `config/settings.py` has been updated with comments guiding users on setting this environment variable.
    - **Error Handling:**
        - Catches and handles `requests` library exceptions (e.g., `Timeout`, `HTTPError`, general `RequestException`).
        - Parses and handles error messages or notes provided by the Alpha Vantage API in its JSON response (e.g., for invalid symbols, rate limits).
        - Handles unexpected or incomplete JSON response structures.
        - Prints informative error messages to the console.
    - **Unit Tests:**
        - Added to `AgentWorkbench/tests/test_finance_skill.py`.
        - Tests mock the `requests.get` calls to the Alpha Vantage API.
        - Coverage includes successful price retrieval, behavior with missing API key, handling of various simulated API error messages (e.g., "Error Message", "Note"), network errors, and malformed/incomplete API responses.
    - **Potential Future Enhancements:**
        - Implement other actions like fetching historical data, company overview, or market news.
        - Support for other financial instruments (e.g., ETFs, cryptocurrencies if covered by the API).
        - More sophisticated parsing of financial data (e.g., converting price to float, handling different currencies if API provides that info).
        - Configuration of the API endpoint or specific API parameters via `config/settings.py`.
- **`LLMSkill` (Phase 2 - Initial Implementation Completed):**
    - **Current State:** Basic text generation functionality implemented.
    - **Functionality Added:**
        - Integrates with OpenAI's API using the `openai` Python library (specifically `ChatCompletion` with models like `gpt-3.5-turbo`).
        - The `execute` method takes a `prompt`, and optional `max_tokens` and `temperature` arguments.
        - Returns the generated text string or `None` on failure.
    - **API Key Management:**
        - Expects the OpenAI API key to be set as an environment variable `OPENAI_API_KEY`.
        - The skill checks for this variable and provides a warning if not set.
        - `config/settings.py` has been updated with comments guiding users on setting this environment variable.
    - **Error Handling:**
        - Catches and handles specific OpenAI API errors (`AuthenticationError`, `RateLimitError`, `APIConnectionError`, `APIStatusError`) as well as general exceptions.
        - Prints informative error messages to the console.
    - **Unit Tests:**
        - Added to `AgentWorkbench/tests/test_llm_skill.py`.
        - Tests mock the `openai.OpenAI` client and its `chat.completions.create` method.
        - Coverage includes successful API calls, handling of custom parameters, behavior with missing API key, and various simulated API error conditions.
    - **Potential Future Enhancements:**
        - Support for different LLM tasks (e.g., summarization, translation (though there's a separate `TranslationSkill`), few-shot prompting).
        - Configuration of different models (e.g., GPT-4, other model providers) via `config/settings.py` or skill parameters.
        - More sophisticated prompt templating or management.
        - Streaming responses.
        - Conversation history management for chat-based interactions.
- **`TranslationSkill` (Phase 2 - Initial Implementation Completed):**
    - **Current State:** Basic translation functionality implemented.
    - **Functionality Added:**
        - Integrates with the `translators` Python library to perform translations. This library attempts to use free tiers of various online translation services (e.g., Google, Bing, Deepl).
        - The `execute` method takes `text_to_translate` (string), `target_language` (string, e.g., "fr", "es"), and an optional `source_language` (string, defaults to "auto" for auto-detection by the library).
        - Returns the translated string or `None` on failure.
    - **API Key Management:**
        - No direct API key management is implemented in this skill, as the `translators` library handles access to services, often via unofficial API usage or free tiers that don't require explicit user-provided keys for basic operation.
    - **Error Handling:**
        - Catches `translators.TranslatorError` for library-specific issues.
        - Catches general exceptions that might occur during the translation process.
        - Prints informative error messages to the console.
    - **Unit Tests:**
        - Added to `AgentWorkbench/tests/test_translation_skill.py`.
        - Tests mock the `translators.translate_text` function.
        - Coverage includes successful translations (with and without specified source language), input validation (empty text/target language), and simulated errors from the translation library.
    - **Potential Future Enhancements:**
        - Allow selection of a specific translation provider (e.g., 'google', 'bing') if the `translators` library supports it and it's beneficial for reliability or quality.
        - More granular error reporting or ability to get supported language codes.
        - Option to configure a specific API key if a premium service via the `translators` library (or a direct API integration) is desired.
- **`WeatherSkill`:**
    - **Current State:** Placeholder.
    - **Potential Enhancements:**
        - Integrate with a weather API (e.g., OpenWeatherMap, WeatherAPI.com) to fetch current weather or forecasts.
        - Methods like `get_current_weather(location)`, `get_forecast(location, days=1)`.
        - Handle location ambiguity and API errors.

### Tools:
- **`DBTool` (`SQLiteTool`):**
    - **Current State:** Implemented as a simple key-value store using SQLite. Tests added.
    - **Potential Enhancements (beyond current K/V scope):**
        - Support for more complex SQL queries if needed by agents (e.g., allowing execution of arbitrary SELECTs, or more structured table interactions). This would require significant changes and careful security considerations (SQL injection).
        - Configuration for different database backends (though this might be overly complex for its current "tool" status).
- **`KnowledgeBaseTool`:**
    - **Current State:** Simple in-memory dictionary. Tests added.
    - **Potential Enhancements:**
        - Option for persistence (e.g., saving/loading to/from a file like JSON or CSV).
        - More advanced query capabilities (e.g., fuzzy matching for questions, semantic search if integrated with embeddings).
        - Could potentially use `SQLiteTool` as a backend for persistence.

## 4. General Approach for Maturing Components
- **Define Scope:** Clearly define the target functionality for the specific skill/tool being matured.
- **Identify Data Sources/APIs:** Research and select appropriate external services if needed.
- **Implement Core Logic:** Write the code to achieve the defined functionality.
- **Robust Error Handling:** Implement comprehensive error handling for both internal logic and external interactions.
- **Configuration:** Externalize key parameters (API keys, URLs, default behaviors) to `config/settings.py`.
- **Testing:** Develop thorough unit tests, mocking all external dependencies.
- **Documentation:** Update any relevant READMEs or create new documentation for the matured component.

This plan provides a roadmap for systematically improving the capabilities and reliability of AgentWorkbench's skills and tools.
