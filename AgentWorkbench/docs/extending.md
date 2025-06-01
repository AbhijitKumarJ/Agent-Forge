# Extending AgentWorkbench

This guide explains how to add your own agents, skills, and tools to the platform.

## Adding a New Skill
1. Subclass `BaseSkill` in `skills/`:
    ```python
    from core import BaseSkill
    class MySkill(BaseSkill):
        def execute(self, *args, **kwargs):
            # Your logic here
            return "result"
    ```
2. Register it in `skills/__init__.py`:
    ```python
    from .my_skill import MySkill
    __all__.append("MySkill")
    ```

## Adding a New Tool
1. Subclass `BaseTool` in `tools/`:
    ```python
    from core import BaseTool
    class MyTool(BaseTool):
        def use(self, *args, **kwargs):
            # Your logic here
            return "result"
    ```
2. Register it in `tools/__init__.py`:
    ```python
    from .my_tool import MyTool
    __all__.append("MyTool")
    ```

## Adding a New Agent
1. Subclass `BaseAgent` or compose with existing agents in `agents/`:
    ```python
    from core import BaseAgent
    class MyAgent(BaseAgent):
        def run(self, task):
            # Your logic here
            return "done"
    ```
2. Register or import your agent as needed.

## Integrating an External API
- Follow the pattern in `skills/` (see `WikipediaSkill`, `FinanceSkill`, etc.).
- Use the `requests` package for HTTP APIs.
- Handle API keys securely (use environment variables).

## Testing
- Add tests in `tests/` for your new components.
- Use `unittest` or your preferred framework.

## UI Integration
- Register your new skill/tool in `skills/__init__.py` or `tools/__init__.py`.
- It will show up in the Streamlit UI automatically.
