import unittest
from agents import SimpleAgent, CollaborativeAgent
from skills import EchoSkill

class TestConsensusProtocol(unittest.TestCase):
    def setUp(self):
        self.agent1 = SimpleAgent(name="A1", description="Echo agent.")
        self.agent1.add_skill(EchoSkill(name="EchoSkill", description="Echoes input."))
        self.agent2 = SimpleAgent(name="A2", description="Echo agent.")
        self.agent2.add_skill(EchoSkill(name="EchoSkill", description="Echoes input."))
        self.agent3 = SimpleAgent(name="A3", description="Echo agent.")
        self.agent3.add_skill(EchoSkill(name="EchoSkill", description="Echoes input."))
        self.collab = CollaborativeAgent(name="Coordinator", description="Consensus demo.",
                                         teammates=[self.agent1, self.agent2, self.agent3])

    def test_majority_voting(self):
        # All agents echo the same, consensus should be that value
        result = self.collab.run("hello")
        self.assertEqual(result, None)  # EchoSkill prints, does not return

    def test_diverse_results(self):
        # Override run to return different values for consensus
        self.agent1.run = lambda task: "yes"
        self.agent2.run = lambda task: "yes"
        self.agent3.run = lambda task: "no"
        result = self.collab.run("vote?")
        self.assertEqual(result, "yes")

if __name__ == "__main__":
    unittest.main()
