# Agent Workbench

A modular, extensible platform for building, experimenting with, and managing AI agents, skills, and tools.

## Features
- Abstract base classes for agents, skills, and tools
- Plug-and-play architecture for rapid prototyping
- Configuration-driven setup
- CLI entry point for agent execution and testing
- Designed for education, research, and practical agent development

## Project Structure
- **/agents**: Concrete agent implementations
- **/skills**: Modular skills for agents
- **/tools**: Tools/utilities that agents can use
- **/core**: Core abstractions and orchestration logic
- **/data**: Data storage (logs, memory, etc.)
- **/config**: Configuration and settings
- **/tests**: Unit/integration tests
- **/docs**: Documentation
- **workbench.py**: Main CLI entry point
- **requirements.txt**: Python dependencies

## Installation
```bash
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

## Usage
```bash
python workbench.py --agent <AgentClass> --task "Your task here"
```

## Extending the Workbench
- Add new agents in `/agents/` by subclassing `BaseAgent`
- Add new skills in `/skills/` by subclassing `BaseSkill`
- Add new tools in `/tools/` by subclassing `BaseTool`
- Register new modules in their respective `__init__.py` files

## Vision
This project is inspired by the "Agent Forge" concept: a learning and experimentation platform for building next-generation AI agents, step-by-step, from foundational concepts to advanced multi-agent systems.

---

For more details, see the [docs](./docs) or the original design plan in `all.md`.
