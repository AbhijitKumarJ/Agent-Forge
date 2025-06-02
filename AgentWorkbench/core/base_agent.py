from abc import ABC, abstractmethod
from typing import List, Any

class BaseAgent(ABC):
    """Abstract base class for all agents."""

    def __init__(self, name: str, description: str, capabilities: List[str] = None, weight: float = 1.0):
        self.name = name
        self.description = description
        self.capabilities = capabilities if capabilities is not None else []
        self.weight = weight
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
        base_str = f"Agent(name={self.name}, description={self.description}, capabilities={self.capabilities}"
        if self.weight != 1.0:
            base_str += f", weight={self.weight}"
        base_str += f", skills={len(self.skills)}, tools={len(self.tools)})"
        return base_str
