import unittest
from unittest.mock import MagicMock
from agents import SimpleAgent, CollaborativeAgent
from skills import EchoSkill, MathSkill, LogSkill # Assuming LogSkill exists for fallback test
from tools import PrintTool

class TestCollaborativeAgent(unittest.TestCase):
    def setUp(self):
        self.agent1 = SimpleAgent(name="Agent1", description="Echo agent.")
        self.agent1.add_skill(EchoSkill(name="EchoSkill", description="Echoes input."))
        self.agent1.add_tool(PrintTool(name="PrintTool", description="Prints input."))

        self.agent2 = SimpleAgent(name="Agent2", description="Math agent.")
        self.agent2.add_skill(MathSkill(name="MathSkill", description="Evaluates math."))
        self.collab = CollaborativeAgent(name="Coordinator", description="Delegates.", teammates=[self.agent1, self.agent2])

    def test_routing_existing_skill(self): # Renamed for clarity
        # Should route math task to agent2
        self.agent2.run = MagicMock(return_value=4) # Mock run for agent2
        self.agent1.run = MagicMock() # Ensure agent1.run is also a mock

        result = self.collab.run("evaluate MathSkill 2+2 calculation") # Task matching skill name
        self.assertEqual(result, 4)
        self.agent2.run.assert_called_once_with("evaluate MathSkill 2+2 calculation")
        self.agent1.run.assert_not_called()


    def test_broadcast_existing_no_match(self): # Renamed for clarity
        # Should broadcast if no clear skill match
        # For broadcast, run will be called on all teammates.
        # The default CollaborativeAgent.run then aggregates.
        # We'll check if agent1 and agent2 run methods are called.
        self.agent1.run = MagicMock(return_value="agent1_res")
        self.agent2.run = MagicMock(return_value="agent2_res")

        # Mock aggregate_results to check what it receives or to control its output
        self.collab.aggregate_results = MagicMock(return_value="aggregated")

        result = self.collab.run("unknown task XYZ")
        self.agent1.run.assert_called_once_with("unknown task XYZ")
        self.agent2.run.assert_called_once_with("unknown task XYZ")
        self.collab.aggregate_results.assert_called_once()
        # Check the actual arguments passed to aggregate_results
        # aggregate_results expects a list of (agent, result) tuples
        args, _ = self.collab.aggregate_results.call_args
        passed_results = args[0]
        self.assertIn((self.agent1, "agent1_res"), passed_results)
        self.assertIn((self.agent2, "agent2_res"), passed_results)
        self.assertEqual(result, "aggregated")


class TestCapabilityRouting(unittest.TestCase):
    def setUp(self):
        # Agent with 'search' capability
        self.search_agent = SimpleAgent(name="SearchAgent", description="Searches web", capabilities=["search"])
        self.search_agent.run = MagicMock(return_value="search_result_news")

        # Agent with 'math' capability and a 'LogSkill'
        self.math_log_agent = SimpleAgent(name="MathLogAgent", description="Does math and logs", capabilities=["math"])
        self.math_log_agent.add_skill(LogSkill(name="LogSkill", description="Logs messages")) # Fallback target
        self.math_log_agent.run = MagicMock(return_value="math_log_agent_ सामान्य_result")


        # Agent with no specific capabilities for these tests, but has an EchoSkill
        self.echo_agent = SimpleAgent(name="EchoAgent", description="Echoes input")
        self.echo_agent.add_skill(EchoSkill(name="EchoSkill", description="Echoes input"))
        self.echo_agent.run = MagicMock(return_value="echo_agent_result")


        self.collab_agent = CollaborativeAgent(
            name="CapabilityCoordinator",
            description="Routes by capability",
            teammates=[self.search_agent, self.math_log_agent, self.echo_agent]
        )
        # Mock aggregate_results for tests where broadcast occurs
        self.collab_agent.aggregate_results = MagicMock(side_effect=lambda x: x[0][1] if x else None)


    def test_routing_to_specific_capability(self):
        """Test routing to an agent based on its capability."""
        task = "search for latest news on AI"
        result = self.collab_agent.run(task)

        self.assertEqual(result, "search_result_news")
        self.search_agent.run.assert_called_once_with(task)
        self.math_log_agent.run.assert_not_called()
        self.echo_agent.run.assert_not_called()

    def test_routing_fallback_to_skill_name(self):
        """Test fallback to skill name matching when capability does not match."""
        task = "Please use LogSkill to record this message" # Matches LogSkill by name

        # Reset math_log_agent mock for this specific test if it could have been called by capability routing
        # (though "LogSkill" isn't a capability here)
        self.math_log_agent.run = MagicMock(return_value="log_skill_run_result")

        result = self.collab_agent.run(task)

        self.assertEqual(result, "log_skill_run_result")
        self.math_log_agent.run.assert_called_once_with(task)
        self.search_agent.run.assert_not_called()
        self.echo_agent.run.assert_not_called()

    def test_routing_broadcast_no_match(self):
        """Test broadcast when no capability or skill/tool name matches."""
        task = "a very unique task that matches nothing specific"

        # Re-mock run methods for all agents to ensure they are distinct for this test
        self.search_agent.run = MagicMock(return_value="search_run_broadcast")
        self.math_log_agent.run = MagicMock(return_value="math_log_run_broadcast")
        self.echo_agent.run = MagicMock(return_value="echo_run_broadcast")

        # Configure aggregate_results for this broadcast scenario
        # It should receive results from all agents. Let's say it picks the first one.
        self.collab_agent.aggregate_results = MagicMock(
            side_effect=lambda res_list: res_list[0][1] if res_list else None
        )

        result = self.collab_agent.run(task)

        self.search_agent.run.assert_called_once_with(task)
        self.math_log_agent.run.assert_called_once_with(task)
        self.echo_agent.run.assert_called_once_with(task)

        self.collab_agent.aggregate_results.assert_called_once()
        args, _ = self.collab_agent.aggregate_results.call_args
        passed_results = args[0]

        # Check that results from all agents were passed to aggregate_results
        # The order might vary, so check for presence
        results_dict = {agent: res for agent, res in passed_results}
        self.assertEqual(results_dict[self.search_agent], "search_run_broadcast")
        self.assertEqual(results_dict[self.math_log_agent], "math_log_run_broadcast")
        self.assertEqual(results_dict[self.echo_agent], "echo_run_broadcast")

        # The result depends on the mock of aggregate_results
        # In this case, it should be the result of the first agent in the teammates list (search_agent)
        self.assertEqual(result, "search_run_broadcast")


if __name__ == "__main__":
    unittest.main()
