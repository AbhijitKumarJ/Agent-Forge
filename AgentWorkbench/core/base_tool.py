from abc import ABC, abstractmethod

class BaseTool(ABC):
    """Abstract base class for all tools."""

    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description

    @abstractmethod
    def use(self, *args, **kwargs):
        """Use the tool (to be implemented by subclasses)."""
        pass

    def __str__(self):
        return f"Tool(name={self.name}, description={self.description})"
