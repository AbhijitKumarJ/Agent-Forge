from core import BaseAgent

class SimpleAgent(BaseAgent):
    """A simple agent that echoes the task and demonstrates skill/tool usage."""

    def run(self, task: str):
        print(f"[SimpleAgent] Task received: {task}")
        # Demonstrate using all skills
        for skill in self.skills:
            print(f"[SimpleAgent] Executing skill: {skill.name}")
            skill.execute(task)
        # Demonstrate using all tools
        for tool in self.tools:
            print(f"[SimpleAgent] Using tool: {tool.name}")
            tool.use(task)
        print(f"[SimpleAgent] Done with task: {task}")
