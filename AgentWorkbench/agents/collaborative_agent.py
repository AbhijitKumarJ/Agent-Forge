from core import BaseAgent
from collections import Counter

class CollaborativeAgent(BaseAgent):
    """An agent that delegates tasks to teammates, routes based on capabilities, and aggregates results."""
    def __init__(self, name, description, teammates=None):
        super().__init__(name, description)
        self.teammates = teammates or []  # List of other agents

    def add_teammate(self, agent):
        self.teammates.append(agent)

    def route_task(self, task: str):
        """Route task to the best teammate based on skills/tools (simple keyword match)."""
        for agent in self.teammates:
            for skill in getattr(agent, 'skills', []):
                if skill.name.lower() in task.lower():
                    return agent
            for tool in getattr(agent, 'tools', []):
                if tool.name.lower() in task.lower():
                    return agent
        return None  # No match

    def aggregate_results(self, results):
        """Aggregate results by majority vote if possible, else return all."""
        if not results:
            return None
        counter = Counter(results)
        most_common = counter.most_common(1)
        if most_common:
            return most_common[0][0]
        return results

    def run(self, task: str):
        print(f"[CollaborativeAgent] Task: {task}")
        # Try routing
        routed_agent = self.route_task(task)
        if routed_agent:
            print(f"[CollaborativeAgent] Routing to agent: {routed_agent.name}")
            result = routed_agent.run(task)
            print(f"[CollaborativeAgent] Routed result: {result}")
            return result
        # Otherwise, broadcast to all
        results = []
        for agent in self.teammates:
            print(f"[CollaborativeAgent] Delegating to: {agent.name}")
            result = agent.run(task)
            results.append((agent.name, result))
        agg = self.aggregate_results([r for _, r in results])
        print(f"[CollaborativeAgent] Aggregated results: {agg}")
        return agg
