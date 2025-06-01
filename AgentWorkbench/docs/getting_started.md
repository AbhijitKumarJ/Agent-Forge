# Getting Started with AgentWorkbench

Welcome to AgentWorkbench! This guide will help you set up, run, and extend the platform.

## Installation
1. Clone the repository.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Running the CLI
- **Single Agent:**
  ```bash
  python workbench.py --task "2+2"
  ```
- **Multi-Agent:**
  ```bash
  python workbench.py --multi --task "What is AI?"
  ```
- **LLM Demo:**
  ```bash
  python workbench.py --llm --task "Write a poem about agents."
  ```

## Running the Streamlit UI
```bash
streamlit run ui_streamlit.py
```
Assign skills/tools and run agents interactively in your browser.

## Setting API Keys
- For LLM and News skills, set environment variables:
  - `OPENAI_API_KEY` for OpenAI
  - `NEWSAPI_KEY` for NewsAPI

## Directory Structure
- `core/`: Abstract base classes
- `agents/`: Agent implementations
- `skills/`: Built-in and API-based skills
- `tools/`: Tools (file, print, DB, etc.)
- `tests/`: Unit and protocol tests
- `docs/`: Guides and documentation

## Next Steps
- See `docs/usage_examples.md` for more examples.
- See `docs/extending.md` to add your own skills, tools, or agents.
