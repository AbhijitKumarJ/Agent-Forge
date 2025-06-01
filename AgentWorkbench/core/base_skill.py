from abc import ABC, abstractmethod

class BaseSkill(ABC):
    """Abstract base class for all skills."""

    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description

    @abstractmethod
    def execute(self, *args, **kwargs):
        """Execute the skill (to be implemented by subclasses)."""
        pass

    def __str__(self):
        return f"Skill(name={self.name}, description={self.description})"
