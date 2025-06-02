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


class TestTaskDecomposition(unittest.TestCase):
    def setUp(self):
        self.agent_a = SimpleAgent(name="AgentA", description="Handles 'part A'")
        self.agent_a.run = MagicMock(return_value="Result from A")

        self.agent_b = SimpleAgent(name="AgentB", description="Handles 'part B'")
        self.agent_b.run = MagicMock(return_value="Result from B")

        self.agent_c = SimpleAgent(name="AgentC", description="Generic Echo Agent")
        # self.agent_c.add_skill(EchoSkill(name="EchoSkill")) # Not strictly needed if run is mocked
        self.agent_c.run = MagicMock(side_effect=lambda task_string: f"Echo: {task_string}")

        self.collab_agent = CollaborativeAgent(
            name="DecomposerAgent",
            description="Tests task decomposition",
            teammates=[self.agent_a, self.agent_b, self.agent_c]
        )
        # Default route_task mock - can be overridden in specific tests
        self.collab_agent.route_task = MagicMock(return_value=None)

    def test_no_decomposition_fallback_routing(self):
        """Test that a simple task is routed if a route exists (no decomposition)."""
        task = "simple task no keywords"
        self.collab_agent.route_task = MagicMock(side_effect=lambda t: self.agent_c if t == task else None)

        result = self.collab_agent.run(task)

        self.collab_agent.route_task.assert_called_once_with(task)
        self.agent_c.run.assert_called_once_with(task)
        self.assertEqual(result, f"Echo: {task}")

    def test_no_decomposition_fallback_broadcast(self):
        """Test broadcast for a simple task if no specific route is found."""
        task = "another simple task"
        self.collab_agent.route_task = MagicMock(return_value=None) # No specific route

        # Mock run methods for broadcast assertion
        self.agent_a.run = MagicMock(return_value="A_broadcast")
        self.agent_b.run = MagicMock(return_value="B_broadcast")
        self.agent_c.run = MagicMock(return_value="C_broadcast")

        # Mock aggregate_results (the main one, not _aggregate_sub_task_results)
        self.collab_agent.aggregate_results = MagicMock(return_value="Broadcasted and aggregated")

        result = self.collab_agent.run(task)

        self.collab_agent.route_task.assert_called_once_with(task)
        self.agent_a.run.assert_called_once_with(task)
        self.agent_b.run.assert_called_once_with(task)
        self.agent_c.run.assert_called_once_with(task)
        self.collab_agent.aggregate_results.assert_called_once()
        self.assertEqual(result, "Broadcasted and aggregated")

    def test_decomposition_with_and_keyword(self):
        """Test task decomposition with ' and ' keyword."""
        task = "do part A and do part B"
        sub_task_a = "do part A"
        sub_task_b = "do part B"

        def route_task_side_effect(t_task):
            if t_task == sub_task_a: return self.agent_a
            if t_task == sub_task_b: return self.agent_b
            return None
        self.collab_agent.route_task = MagicMock(side_effect=route_task_side_effect)

        result = self.collab_agent.run(task)

        self.agent_a.run.assert_called_once_with(sub_task_a)
        self.agent_b.run.assert_called_once_with(sub_task_b)
        self.assertEqual(result, "Result from A\nResult from B")

    def test_decomposition_case_insensitive_and(self):
        """Test task decomposition with case-insensitive ' AND ' keyword."""
        task = "do part A AND do part B"
        sub_task_a = "do part A" # _try_decompose_task preserves casing of subtasks
        sub_task_b = "do part B"

        def route_task_side_effect(t_task):
            if t_task == sub_task_a: return self.agent_a
            if t_task == sub_task_b: return self.agent_b
            return None
        self.collab_agent.route_task = MagicMock(side_effect=route_task_side_effect)

        result = self.collab_agent.run(task)

        self.agent_a.run.assert_called_once_with(sub_task_a)
        self.agent_b.run.assert_called_once_with(sub_task_b)
        self.assertEqual(result, "Result from A\nResult from B")

    def test_decomposition_first_and_only(self):
        """Test decomposition splits only on the first ' and '."""
        task = "part A and part B and part C"
        sub_task_1 = "part A"
        sub_task_2 = "part B and part C" # Second "and" is part of the sub-task

        self.agent_a.run = MagicMock(return_value="Result from A for sub1")
        self.agent_b.run = MagicMock(return_value="Result from B for sub2")

        def route_task_side_effect(t_task):
            if t_task == sub_task_1: return self.agent_a
            if t_task == sub_task_2: return self.agent_b
            return None
        self.collab_agent.route_task = MagicMock(side_effect=route_task_side_effect)

        result = self.collab_agent.run(task)

        self.agent_a.run.assert_called_once_with(sub_task_1)
        self.agent_b.run.assert_called_once_with(sub_task_2)
        self.assertEqual(result, "Result from A for sub1\nResult from B for sub2")

    def test_decomposition_sub_task_cannot_be_routed(self):
        """Test decomposition where one sub-task cannot be routed."""
        task = "do known part A and do unknown part X"
        sub_task_known = "do known part A"
        sub_task_unknown = "do unknown part X"

        def route_task_side_effect(t_task):
            if t_task == sub_task_known: return self.agent_a
            if t_task == sub_task_unknown: return None # Cannot route unknown part
            return None
        self.collab_agent.route_task = MagicMock(side_effect=route_task_side_effect)

        result = self.collab_agent.run(task)

        self.agent_a.run.assert_called_once_with(sub_task_known)
        expected_result = f"Result from A\n[Sub-task '{sub_task_unknown}' could not be routed]"
        self.assertEqual(result, expected_result)

    def test_decomposition_sub_task_agent_fails(self):
        """Test decomposition where one sub-task's assigned agent fails."""
        task = "part A good and part B bad"
        sub_task_good = "part A good"
        sub_task_bad = "part B bad"

        self.agent_a.run = MagicMock(return_value="Result from A good")
        self.agent_b.run = MagicMock(side_effect=Exception("Agent B internal error"))

        def route_task_side_effect(t_task):
            if t_task == sub_task_good: return self.agent_a
            if t_task == sub_task_bad: return self.agent_b
            return None
        self.collab_agent.route_task = MagicMock(side_effect=route_task_side_effect)

        result = self.collab_agent.run(task)

        self.agent_a.run.assert_called_once_with(sub_task_good)
        self.agent_b.run.assert_called_once_with(sub_task_bad)

        # The error message format is: f"[{error_msg}]" where error_msg is f"Error executing sub-task '{sub_task_string}' by {routed_agent.name}: {e}"
        expected_error_part = f"[Error executing sub-task '{sub_task_bad}' by AgentB: Agent B internal error]"
        expected_result = f"Result from A good\n{expected_error_part}"
        self.assertEqual(result, expected_result)


if __name__ == "__main__":
    unittest.main()
