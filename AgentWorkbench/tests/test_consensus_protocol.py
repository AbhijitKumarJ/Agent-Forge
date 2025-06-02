import unittest
from unittest.mock import MagicMock # Added for mocking run methods if needed for clarity
from agents import SimpleAgent, CollaborativeAgent
from skills import EchoSkill

class TestConsensusProtocol(unittest.TestCase):
    def setUp(self):
        # Default weight is 1.0, these agents will have it.
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
        # Here, agents have default weight 1.0, so it's also a weighted vote test.
        self.agent1.run = lambda task: "hello"
        self.agent2.run = lambda task: "hello"
        self.agent3.run = lambda task: "hello"
        result = self.collab.run("hello task")
        self.assertEqual(result, "hello")

    def test_diverse_results_majority_vote_fallback_or_equal_weights(self):
        # This test implicitly relies on either equal weights (default 1.0) or fallback if weights were missing.
        # Given all agents are SimpleAgents, they will have weight=1.0 by default.
        self.agent1.run = lambda task: "yes"
        self.agent2.run = lambda task: "yes"
        self.agent3.run = lambda task: "no"
        result = self.collab.run("vote?")
        self.assertEqual(result, "yes")


class TestWeightedVotingConsensus(unittest.TestCase):
    def test_weighted_voting_overrides_majority(self):
        agent_A = SimpleAgent(name="AgentA", description="Weighted Agent A", weight=2.0)
        agent_A.run = lambda task: "yes"
        agent_B = SimpleAgent(name="AgentB", description="Weighted Agent B", weight=0.5)
        agent_B.run = lambda task: "no"
        agent_C = SimpleAgent(name="AgentC", description="Weighted Agent C", weight=0.5)
        agent_C.run = lambda task: "no"

        collab = CollaborativeAgent(name="WeightedVoteCoord", description="Tests weighted voting",
                                    teammates=[agent_A, agent_B, agent_C])
        result = collab.run("Decision task")
        self.assertEqual(result, "yes") # "yes" (2.0) vs "no" (0.5+0.5=1.0)

    def test_weighted_voting_equal_weights_is_majority(self):
        agent_A = SimpleAgent(name="AgentA", description="Equal Weight A", weight=1.0)
        agent_A.run = lambda task: "yes"
        agent_B = SimpleAgent(name="AgentB", description="Equal Weight B", weight=1.0)
        agent_B.run = lambda task: "yes"
        agent_C = SimpleAgent(name="AgentC", description="Equal Weight C", weight=1.0)
        agent_C.run = lambda task: "no"

        collab = CollaborativeAgent(name="EqualWeightCoord", description="Tests equal weights",
                                    teammates=[agent_A, agent_B, agent_C])
        result = collab.run("Decision task")
        self.assertEqual(result, "yes") # "yes" (1.0+1.0=2.0) vs "no" (1.0)

    def test_fallback_to_majority_if_weights_missing_or_none(self):
        agent_A = SimpleAgent(name="AgentA", description="Weighted Agent A", weight=2.0)
        agent_A.run = lambda task: "yes" # High weight but will be ignored

        agent_B = SimpleAgent(name="AgentB", description="No Weight Agent B")
        agent_B.run = lambda task: "no"
        agent_B.weight = None # Explicitly set weight to None to trigger fallback

        agent_C = SimpleAgent(name="AgentC", description="Default Weight Agent C") # weight = 1.0
        agent_C.run = lambda task: "no"
        # To ensure fallback, at least one agent in the decision path must have weight=None.
        # The logic is: if *any* agent involved in results has no weight, it falls back.
        # So, if agent_B participates, its None weight should trigger fallback.

        collab = CollaborativeAgent(name="FallbackCoord", description="Tests fallback",
                                    teammates=[agent_A, agent_B, agent_C])

        # In a broadcast scenario, all agents participate.
        # agent_A returns "yes", agent_B returns "no", agent_C returns "no"
        # Fallback: "yes" (1 vote), "no" (2 votes) -> "no"
        result = collab.run("Decision task for fallback")
        self.assertEqual(result, "no")


    def test_weighted_voting_non_hashable_results(self):
        agent_A = SimpleAgent(name="AgentA", description="Non-hashable A", weight=2.0)
        agent_A.run = lambda task: ["alpha", "beta"] # List is non-hashable
        agent_B = SimpleAgent(name="AgentB", description="Non-hashable B", weight=1.0)
        agent_B.run = lambda task: ["gamma"]

        collab = CollaborativeAgent(name="NonHashableCoord", description="Tests non-hashable",
                                    teammates=[agent_A, agent_B])
        result = collab.run("Task with non-hashable results")
        # aggregate_results should convert list to tuple for key
        self.assertEqual(result, ("alpha", "beta")) # Expecting tuple due to internal conversion

    def test_weighted_voting_tie_resolution(self):
        """Test how ties are handled in weighted voting (first one wins)."""
        agent_A = SimpleAgent(name="AgentA", description="Tie Agent A", weight=1.0)
        agent_A.run = lambda task: "result_A"
        agent_B = SimpleAgent(name="AgentB", description="Tie Agent B", weight=1.0)
        agent_B.run = lambda task: "result_B"
        agent_C = SimpleAgent(name="AgentC", description="Tie Agent C", weight=0.5) # Lower weight
        agent_C.run = lambda task: "result_C"

        # Teammates order: A, B, C. If A and B tie, A's result should be chosen by max()
        collab1 = CollaborativeAgent(name="TieCoord1", description="Tests tie resolution",
                                     teammates=[agent_A, agent_B, agent_C])
        result1 = collab1.run("Tie task")
        self.assertEqual(result1, "result_A")

        # Teammates order: B, A, C. If B and A tie, B's result should be chosen
        collab2 = CollaborativeAgent(name="TieCoord2", description="Tests tie resolution",
                                     teammates=[agent_B, agent_A, agent_C])
        result2 = collab2.run("Tie task")
        self.assertEqual(result2, "result_B")


if __name__ == "__main__":
    unittest.main()
