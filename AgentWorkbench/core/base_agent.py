from abc import ABC, abstractmethod
from typing import List, Any

class BaseAgent(ABC):
    """Abstract base class for all agents."""

    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.skills: List[Any] = []
        self.tools: List[Any] = []

    def add_skill(self, skill):
        """Attach a skill to the agent."""
        self.skills.append(skill)

    def add_tool(self, tool):
        """Attach a tool to the agent."""
        self.tools.append(tool)

    @abstractmethod
    def run(self, task: str):
        """Run the agent to perform a given task (to be implemented by subclasses)."""
        pass

    def __str__(self):
        return f"Agent(name={self.name}, description={self.description}, skills={len(self.skills)}, tools={len(self.tools)})"
