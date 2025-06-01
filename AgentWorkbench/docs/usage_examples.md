# Usage Examples

This guide provides practical examples for using AgentWorkbench.

## 1. Run a MathBot Agent (CLI)
```bash
python workbench.py --task "5 * (3 + 2)"
```

## 2. Run Multi-Agent Consensus Demo (CLI)
```bash
python workbench.py --multi --task "What is the capital of France?"
```

## 3. Use LLM Skill (CLI)
```bash
python workbench.py --llm --task "Explain reinforcement learning."
```

## 4. Run the Streamlit UI
```bash
streamlit run ui_streamlit.py
```
- Assign skills/tools to agents and teammates.
- Try WikipediaSkill, TranslationSkill, FinanceSkill, etc.
- See consensus/voting breakdown for collaborative agents.

## 5. Save Web Search Results to a File
- Assign WebSearchSkill and FileTool to an agent.
- Task: `"Python programming language"`
- The agent will search and save the result to a file.

## 6. Distributed Knowledge Base Demo
- Assign SQLiteTool to multiple agents (in UI or CLI).
- Agents will share and persist knowledge using the same SQLite DB file.

## 7. Custom Agent Example (Python)
```python
from agents.sample_agents import create_math_bot
agent = create_math_bot()
agent.run("12 / 4")
```
