import unittest
from agents import SimpleAgent, CollaborativeAgent
from skills import EchoSkill, MathSkill
from tools import PrintTool

class TestCollaborativeAgent(unittest.TestCase):
    def setUp(self):
        self.agent1 = SimpleAgent(name="Agent1", description="Echo agent.")
        self.agent1.add_skill(EchoSkill(name="EchoSkill", description="Echoes input."))
        self.agent1.add_tool(PrintTool(name="PrintTool", description="Prints input."))

        self.agent2 = SimpleAgent(name="Agent2", description="Math agent.")
        self.agent2.add_skill(MathSkill(name="MathSkill", description="Evaluates math."))
        self.collab = CollaborativeAgent(name="Coordinator", description="Delegates.", teammates=[self.agent1, self.agent2])

    def test_routing(self):
        # Should route math task to agent2
        result = self.collab.run("2+2")
        self.assertEqual(result, 4)

    def test_broadcast(self):
        # Should broadcast if no clear skill match
        result = self.collab.run("unknown task")
        self.assertIsNotNone(result)

if __name__ == "__main__":
    unittest.main()
