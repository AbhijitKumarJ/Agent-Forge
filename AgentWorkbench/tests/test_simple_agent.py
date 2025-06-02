import unittest
from agents import SimpleAgent
from skills import EchoSkill
from tools import PrintTool

class TestSimpleAgent(unittest.TestCase):
    def setUp(self):
        self.agent = SimpleAgent(name="TestAgent", description="Test agent.")
        self.skill = EchoSkill(name="EchoSkill", description="Echoes input.")
        self.tool = PrintTool(name="PrintTool", description="Prints input.")
        self.agent.add_skill(self.skill)
        self.agent.add_tool(self.tool)

    def test_run(self):
        # This test checks that run executes without error
        try:
            self.agent.run("Test task")
        except Exception as e:
            self.fail(f"Agent run raised exception: {e}")

if __name__ == "__main__":
    unittest.main()
