import unittest
import json # Added
from unittest.mock import MagicMock, patch
from agents import SimpleAgent, CollaborativeAgent
from skills import EchoSkill, MathSkill, LogSkill, LLMSkill # Added LLMSkill
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
        # Worker agents
        self.agent_a = SimpleAgent(name="AgentA", description="Worker A")
        self.agent_a.run = MagicMock(return_value="Result from A")
        self.agent_b = SimpleAgent(name="AgentB", description="Worker B")
        self.agent_b.run = MagicMock(return_value="Result from B")

        # Agent with LLMSkill
        self.llm_agent = SimpleAgent(name="LLMAgent", description="Agent with LLM Skill")
        self.llm_skill_mock = MagicMock(spec=LLMSkill) # Mock the LLMSkill instance
        self.llm_skill_mock.name = "LLMSkill" # Give the mock a name attribute
        self.llm_agent.add_skill(self.llm_skill_mock)
        self.llm_agent.run = MagicMock() # LLMAgent itself doesn't run, its skill is used

        self.collab_agent = CollaborativeAgent(
            name="DecomposerAgent",
            description="Tests LLM task decomposition",
            teammates=[self.llm_agent, self.agent_a, self.agent_b] # LLM agent is a teammate
        )
        # Mock route_task for sub-tasks by default, can be overridden
        self.collab_agent.route_task = MagicMock(return_value=None)

    def test_no_decomposition_llm_skill_not_found_fallback_routing(self):
        """Test fallback routing when no LLM agent is available."""
        task = "simple task, no llm agent involved"
        # Create a collab agent without the LLM agent
        collab_no_llm = CollaborativeAgent("NoLLM", "Test", teammates=[self.agent_a, self.agent_b])
        collab_no_llm.route_task = MagicMock(side_effect=lambda t: self.agent_a if t == task else None)
        self.agent_a.run = MagicMock(return_value="Fallback for no LLM")

        result = collab_no_llm.run(task)

        self.agent_a.run.assert_called_once_with(task)
        self.assertEqual(result, "Fallback for no LLM")
        self.llm_skill_mock.execute.assert_not_called() # Ensure LLM was not called

    def test_no_decomposition_llm_skill_fails_fallback_routing(self):
        """Test fallback routing when LLM skill execution fails."""
        task = "task causing llm error"
        self.llm_skill_mock.execute.side_effect = Exception("LLM API Error")

        # If LLM decomposition fails, it should try to route the original task
        self.collab_agent.route_task = MagicMock(side_effect=lambda t: self.agent_a if t == task else None)
        self.agent_a.run = MagicMock(return_value="Fallback due to LLM error")

        result = self.collab_agent.run(task)

        self.llm_skill_mock.execute.assert_called_once() # LLM was called
        self.agent_a.run.assert_called_once_with(task) # Fallback to routing original task
        self.assertEqual(result, "Fallback due to LLM error")

    def test_no_decomposition_llm_invalid_json_fallback_routing(self):
        """Test fallback routing when LLM returns invalid JSON."""
        task = "task causing bad json"
        self.llm_skill_mock.execute.return_value = "this is not json"

        self.collab_agent.route_task = MagicMock(side_effect=lambda t: self.agent_a if t == task else None)
        self.agent_a.run = MagicMock(return_value="Fallback due to bad JSON")

        result = self.collab_agent.run(task)

        self.llm_skill_mock.execute.assert_called_once()
        self.agent_a.run.assert_called_once_with(task)
        self.assertEqual(result, "Fallback due to bad JSON")

    def test_no_decomposition_llm_returns_atomic_task_empty_list(self):
        """Test fallback routing when LLM returns an empty list (atomic task)."""
        task = "simple atomic task"
        self.llm_skill_mock.execute.return_value = json.dumps([])

        self.collab_agent.route_task = MagicMock(side_effect=lambda t: self.agent_a if t == task else None)
        self.agent_a.run = MagicMock(return_value="Atomic Result A")

        result = self.collab_agent.run(task)

        self.llm_skill_mock.execute.assert_called_once()
        self.agent_a.run.assert_called_once_with(task)
        self.assertEqual(result, "Atomic Result A")

    def test_no_decomposition_llm_returns_list_of_blank_strings(self):
        """Test fallback routing when LLM returns a list of only blank strings."""
        task = "task leading to blank subtasks"
        self.llm_skill_mock.execute.return_value = json.dumps(["", "   "])

        self.collab_agent.route_task = MagicMock(side_effect=lambda t: self.agent_a if t == task else None)
        self.agent_a.run = MagicMock(return_value="Fallback from blank strings")

        result = self.collab_agent.run(task)

        self.llm_skill_mock.execute.assert_called_once()
        self.agent_a.run.assert_called_once_with(task)
        self.assertEqual(result, "Fallback from blank strings")

    def test_no_decomposition_fallback_broadcast(self):
        """Test broadcast when LLM decomposition fails and no route for original task."""
        task = "another simple task for broadcast"
        self.llm_skill_mock.execute.return_value = json.dumps([]) # LLM says atomic

        self.collab_agent.route_task = MagicMock(return_value=None) # No specific route for original task

        self.agent_a.run = MagicMock(return_value="A_broadcast_llm_fallback")
        self.agent_b.run = MagicMock(return_value="B_broadcast_llm_fallback")
        # LLMAgent's own run method won't be called if it's just providing the skill
        # but if it's also a general teammate, it might. Here, it's simpler if it doesn't participate in broadcast.
        # Let's assume self.llm_agent is not a general worker for this broadcast.
        # We can re-init collab_agent for this test if needed, or ensure llm_agent.run is not called.
        # For simplicity, let's assume only agent_a and agent_b are general workers.
        # We need to ensure llm_agent.run isn't called by broadcast.
        # The current setup has llm_agent in teammates.
        # Let's re-mock its run if it's part of broadcast.
        self.llm_agent.run = MagicMock(return_value="LLM_agent_broadcast_res")


        self.collab_agent.aggregate_results = MagicMock(return_value="Broadcasted and aggregated after LLM fallback")

        result = self.collab_agent.run(task)

        self.llm_skill_mock.execute.assert_called_once()
        self.collab_agent.route_task.assert_called_once_with(task) # Attempted to route original task
        self.agent_a.run.assert_called_once_with(task)
        self.agent_b.run.assert_called_once_with(task)
        self.llm_agent.run.assert_called_once_with(task) # Since it's in teammates
        self.collab_agent.aggregate_results.assert_called_once()
        self.assertEqual(result, "Broadcasted and aggregated after LLM fallback")

    def test_llm_decomposition_successful(self):
        """Test successful LLM decomposition and sub-task execution."""
        task = "complex task for llm"
        sub_task_1 = "sub-task 1"
        sub_task_2 = "sub-task 2"
        expected_sub_tasks = [sub_task_1, sub_task_2]

        self.llm_skill_mock.execute.return_value = json.dumps(expected_sub_tasks)

        self.agent_a.run = MagicMock(return_value="Result A from sub1")
        self.agent_b.run = MagicMock(return_value="Result B from sub2")

        def route_task_side_effect(t_task):
            if t_task == sub_task_1: return self.agent_a
            if t_task == sub_task_2: return self.agent_b
            return None
        self.collab_agent.route_task = MagicMock(side_effect=route_task_side_effect)

        result = self.collab_agent.run(task)

        self.llm_skill_mock.execute.assert_called_once()
        # route_task is called for each sub-task
        self.assertEqual(self.collab_agent.route_task.call_count, len(expected_sub_tasks))
        self.collab_agent.route_task.assert_any_call(sub_task_1)
        self.collab_agent.route_task.assert_any_call(sub_task_2)

        self.agent_a.run.assert_called_once_with(sub_task_1)
        self.agent_b.run.assert_called_once_with(sub_task_2)
        self.assertEqual(result, "Result A from sub1\nResult B from sub2")

    def test_llm_decomposition_sub_task_cannot_be_routed(self):
        """Test LLM decomposition where one sub-task cannot be routed."""
        task = "do known part A and do unknown part X with LLM"
        sub_task_known = "do known part A"
        sub_task_unknown = "do unknown part X"
        expected_sub_tasks = [sub_task_known, sub_task_unknown]

        self.llm_skill_mock.execute.return_value = json.dumps(expected_sub_tasks)
        self.agent_a.run = MagicMock(return_value="Result A for known sub")


        def route_task_side_effect(t_task):
            if t_task == sub_task_known: return self.agent_a
            if t_task == sub_task_unknown: return None # Cannot route unknown part
            return None
        self.collab_agent.route_task = MagicMock(side_effect=route_task_side_effect)

        result = self.collab_agent.run(task)

        self.llm_skill_mock.execute.assert_called_once()
        self.agent_a.run.assert_called_once_with(sub_task_known)
        # Check that agent_b (or any other for unknown part) was not called
        self.agent_b.run.assert_not_called()

        expected_result_str = f"Result A for known sub\n[Sub-task '{sub_task_unknown}' could not be routed]"
        self.assertEqual(result, expected_result_str)

    def test_llm_decomposition_sub_task_agent_fails(self):
        """Test LLM decomposition where one sub-task's assigned agent fails."""
        task = "part A good and part B bad with LLM"
        sub_task_good = "part A good"
        sub_task_bad = "part B bad"
        expected_sub_tasks = [sub_task_good, sub_task_bad]

        self.llm_skill_mock.execute.return_value = json.dumps(expected_sub_tasks)

        self.agent_a.run = MagicMock(return_value="Result from A good via LLM")
        self.agent_b.run = MagicMock(side_effect=Exception("Agent B LLM sub-task error"))

        def route_task_side_effect(t_task):
            if t_task == sub_task_good: return self.agent_a
            if t_task == sub_task_bad: return self.agent_b
            return None
        self.collab_agent.route_task = MagicMock(side_effect=route_task_side_effect)

        result = self.collab_agent.run(task)

        self.llm_skill_mock.execute.assert_called_once()
        self.agent_a.run.assert_called_once_with(sub_task_good)
        self.agent_b.run.assert_called_once_with(sub_task_bad)

        expected_error_part = f"[Error executing sub-task '{sub_task_bad}' by AgentB: Agent B LLM sub-task error]"
        expected_result_str = f"Result from A good via LLM\n{expected_error_part}"
        self.assertEqual(result, expected_result_str)


if __name__ == "__main__":
    unittest.main()
