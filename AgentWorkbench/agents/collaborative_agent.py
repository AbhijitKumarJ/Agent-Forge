import json
from core import BaseAgent
from collections import Counter
from typing import List, Any, Optional, Tuple
from ..skills import LLMSkill # Adjusted import path assuming skills is a sibling directory to agents


class CollaborativeAgent(BaseAgent):
    """
    A specialized agent that coordinates tasks among a team of other agents.

    The CollaborativeAgent acts as a manager or a delegator. Its key functionalities include:
    1.  **LLM-Driven Task Decomposition**: It attempts to decompose complex tasks
        into simpler, actionable sub-tasks. This process relies on a teammate
        equipped with an `LLMSkill`. If decomposition is successful, each
        sub-task is then routed and executed individually.
    2.  **Capability-Based Routing**: If task decomposition is not performed or
        is unsuccessful, the agent routes the entire task to a specific teammate.
        This routing primarily considers the declared `capabilities` of teammates.
    3.  **Skill/Tool Fallback Routing**: If capability-based routing yields no match,
        it falls back to matching task keywords against teammates' skill and tool names.
    4.  **Broadcast**: If no specific agent can be identified for a task, it is
        broadcast to all teammates.
    5.  **Result Aggregation**: Results from multiple teammates (from broadcast) are
        aggregated using weighted voting (if agent `weight` attributes are set)
        or by a simple majority vote. Results from decomposed sub-tasks are
        currently combined by simple string concatenation.

    Attributes:
        teammates (List[BaseAgent]): A list of agent objects that are part of the team.
    """
    def __init__(self, *args, teammates: Optional[List[BaseAgent]] = None, **kwargs):
        """
        Initializes the CollaborativeAgent.

        Args:
            *args: Positional arguments to be passed to the BaseAgent constructor
                   (e.g., name, description).
            teammates (Optional[List[BaseAgent]]): A list of agent instances that
                will be part of this collaborative team. Defaults to an empty list.
            **kwargs: Keyword arguments to be passed to the BaseAgent constructor
                      (e.g., capabilities, weight).
        """
        super().__init__(*args, **kwargs)
        self.teammates: List[BaseAgent] = teammates if teammates is not None else []

    def add_teammate(self, agent: BaseAgent):
        """
        Adds an agent to the collaborative team.

        Args:
            agent (BaseAgent): The agent instance to be added to the team.
        """
        self.teammates.append(agent)

    def route_task(self, task: str) -> Optional[BaseAgent]:
        """
        Routes a task to the most suitable teammate based on a predefined strategy.

        The routing logic is as follows:
        1.  **Capability Matching**: It first iterates through teammates. If an agent
            has a `capabilities` list (strings defining its specializations),
            the method checks if any keyword from the agent's capabilities is
            present (case-insensitive) in the `task` string. The first agent
            found with a matching capability is chosen.
        2.  **Skill/Tool Name Matching (Fallback)**: If no agent is found based on
            capabilities, it falls back to checking skill and tool names. It
            iterates through teammates again. For each agent, it checks if any of
            its skill names or tool names (case-insensitive) are present in the
            `task` string. The first agent found with a matching skill or tool
            name is chosen.
        3.  **No Match**: If no suitable agent is found by either method,
            `None` is returned.

        Args:
            task (str): The task description string.

        Returns:
            Optional[BaseAgent]: The agent best suited for the task, or None if no
                                 specific agent is identified.
        """
        # 1. Try routing based on capabilities
        for agent in self.teammates:
            if hasattr(agent, 'capabilities') and agent.capabilities:
                for capability in agent.capabilities:
                    if capability.lower() in task.lower():
                        print(f"[CollaborativeAgent] Routing to {agent.name} based on capability: {capability}")
                        return agent

        # 2. Fallback to skill/tool name matching
        for agent in self.teammates:
            for skill in getattr(agent, 'skills', []):
                if skill.name.lower() in task.lower():
                    print(f"[CollaborativeAgent] Routing to {agent.name} based on skill: {skill.name}")
                    return agent
            for tool in getattr(agent, 'tools', []):
                if tool.name.lower() in task.lower():
                    print(f"[CollaborativeAgent] Routing to {agent.name} based on tool: {tool.name}")
                    return agent

        print("[CollaborativeAgent] No suitable agent found for routing.")
        return None  # No match

    def _try_decompose_task(self, task: str) -> Optional[List[str]]:
        """
        Attempts to decompose a task into sub-tasks using an LLM-equipped teammate.

        This method searches for a teammate that possesses an `LLMSkill`. If found,
        it constructs a detailed prompt asking the LLM to break down the given `task`
        into a list of simpler, actionable sub-task strings. The LLM is expected
        to return this list in JSON format (e.g., `["sub_task1", "sub_task2"]`).

        The method handles several potential failure points:
        -   If no teammate with an `LLMSkill` is found, decomposition is skipped.
        -   If the LLM call (via the `LLMSkill.execute()` method) fails or returns
            no response.
        -   If the LLM's response is not valid JSON or does not conform to the
            expected format (a list of strings).

        If the LLM considers the task atomic and not decomposable, it's expected
        to return an empty list (`[]`), which this method will pass on. The `run`
        method will then handle this by processing the original task.

        The previous keyword-based decomposition logic has been removed.

        Args:
            task (str): The task string to be decomposed.

        Returns:
            Optional[List[str]]: A list of sub-task strings if decomposition is
                                 successful (this list can be empty if the LLM
                                 deems the task atomic). Returns `None` if an
                                 `LLMSkill`-equipped teammate is not found, or if
                                 any error occurs during the LLM call or response processing.
        """
        llm_skill_agent = None
        llm_skill_instance = None

        for teammate in self.teammates:
            for skill in getattr(teammate, 'skills', []):
                if isinstance(skill, LLMSkill):
                    llm_skill_agent = teammate
                    llm_skill_instance = skill
                    break
            if llm_skill_agent:
                break

        if not llm_skill_agent or not llm_skill_instance:
            print("[CollaborativeAgent] No teammate with LLMSkill found. Skipping LLM-based decomposition.")
            return None

        prompt = f"""You are an expert task decomposition assistant. Your goal is to break down a complex user task into a series of simpler, actionable sub-tasks. These sub-tasks should be executable by different specialized agents.

Analyze the following user task and provide a list of sub-tasks in JSON format. The JSON output should be a list of strings, where each string is a sub-task.

User Task: "{task}"

If the task is already simple and cannot or should not be decomposed, return an empty list [].
If the task implies a clear sequence, maintain that order in the sub-tasks.

Your Output (should be only a valid JSON list of strings):"""

        print(f"[CollaborativeAgent] Attempting LLM-based task decomposition using {llm_skill_agent.name}'s LLMSkill.")

        llm_response = None
        try:
            # BaseSkill defines execute, not run.
            llm_response = llm_skill_instance.execute(prompt)
        except Exception as e:
            print(f"[CollaborativeAgent] Error during LLM call for task decomposition: {e}")
            return None

        if not llm_response:
            print("[CollaborativeAgent] LLM returned no response for decomposition.")
            return None

        print(f"[CollaborativeAgent] LLM response for decomposition: {llm_response}")

        try:
            # Attempt to strip potential markdown code block fences if LLM wraps JSON in them
            clean_response = llm_response.strip()
            if clean_response.startswith("```json"):
                clean_response = clean_response[len("```json"):].strip()
            if clean_response.endswith("```"):
                clean_response = clean_response[:-len("```")].strip()

            sub_tasks = json.loads(clean_response)
        except json.JSONDecodeError as e:
            print(f"[CollaborativeAgent] Failed to parse LLM response as JSON: {e}. Response: {llm_response}")
            return None

        if not isinstance(sub_tasks, list):
            print(f"[CollaborativeAgent] LLM response is not a list. Response: {sub_tasks}")
            return None

        if not all(isinstance(st, str) for st in sub_tasks):
            print(f"[CollaborativeAgent] Not all items in LLM response list are strings. Response: {sub_tasks}")
            return None

        # It's okay to return an empty list if the LLM deems the task non-decomposable.
        # The run method will handle an empty sub_tasks list (likely by falling back to original task).
        # Or if it contains only empty strings after stripping (though the prompt asks for non-empty)
        # valid_sub_tasks = [st.strip() for st in sub_tasks if st.strip()]
        # if not valid_sub_tasks and sub_tasks: # if sub_tasks was not empty but all items were whitespace
        #    print(f"[CollaborativeAgent] LLM decomposition resulted in empty or whitespace-only sub-tasks.")
        #    return [] # Return empty list, let run method handle this.

        print(f"[CollaborativeAgent] Successfully decomposed task into: {sub_tasks}")
        return sub_tasks

    def _aggregate_sub_task_results(self, sub_task_results: list) -> str:
        """
        Aggregates results from successfully executed sub-tasks.

        Currently, this method converts all sub-task results to strings and
        concatenates them, separated by a newline character.

        Args:
            sub_task_results (list): A list of results from executed sub-tasks.
                                     Items can be of any type that `map(str, ...)` can handle.

        Returns:
            str: A single string combining all sub-task results, each on a new line.
        """
        print(f"[CollaborativeAgent] Aggregating sub-task results: {sub_task_results}")
        return "\n".join(map(str, sub_task_results))

    def aggregate_results(self, agent_results: List[Tuple[BaseAgent, Any]]) -> Any:
        """
        Aggregates results obtained from multiple agents.

        The method uses weighted voting if all participating agents have a valid
        `weight` attribute (float). Otherwise, it falls back to a simple majority vote.

        Args:
            agent_results (List[Tuple[BaseAgent, Any]]): A list of tuples, where
                each tuple contains the agent object that produced the result and
                the result itself (e.g., `[(agent1, 'yes'), (agent2, 'no')]`).

        Returns:
            Any: The aggregated result. This could be the result with the highest
                 weighted score, the result with the simple majority, or one of
                 the results if there's a tie or no clear winner. Returns `None`
                 if `agent_results` is empty.

        Weighted Voting Mechanism:
            - Each agent's result is weighted by the agent's `weight` attribute.
            - Scores for each unique result are summed up based on the weights of
              the agents that proposed them.
            - The result with the highest total weighted score is chosen.
            - Non-hashable results (like lists or dictionaries) are converted to
              hashable representations (tuples) to be used as keys in the scoring
              dictionary. For lists, this means `tuple(list_val)`. For dicts,
              this means `tuple(sorted(dict_val.items()))`.

        Fallback to Majority Vote:
            - If any agent involved in `agent_results` does not have a `weight`
              attribute or if `agent.weight` is `None`, the system falls back to
              a simple majority vote using `collections.Counter` on the raw
              result values.
        """
        if not agent_results:
            return None

        # Check if all agents in results have a weight attribute
        use_weighted_voting = True
        for agent, _ in agent_results:
            if not hasattr(agent, 'weight') or agent.weight is None:
                use_weighted_voting = False
                break

        if use_weighted_voting:
            print("[CollaborativeAgent] Using weighted voting for aggregation.")
            weighted_scores = {}
            for agent, result_val in agent_results:
                # Ensure result_val is hashable for dictionary keys
                # If result_val is a list or dict, convert to tuple or str
                if isinstance(result_val, list):
                    key_val = tuple(result_val)
                elif isinstance(result_val, dict):
                    key_val = tuple(sorted(result_val.items()))
                else:
                    key_val = result_val

                current_score = weighted_scores.get(key_val, 0.0)
                weighted_scores[key_val] = current_score + agent.weight

            if not weighted_scores: # Should not happen if agent_results is not empty
                return None

            # Find the result with the highest score
            # If multiple results have the same highest score, max() returns the first one encountered.
            best_result = max(weighted_scores, key=weighted_scores.get)
            return best_result
        else:
            print("[CollaborativeAgent] Falling back to majority voting for aggregation.")
            # Fallback to existing majority vote (extracting only result values)
            plain_results = [result_val for _, result_val in agent_results]
            if not plain_results: # Should not happen if agent_results is not empty
                return None
            counter = Counter(plain_results)
            most_common = counter.most_common(1)
            if most_common:
                # Counter returns a list of (item, count) tuples
                return most_common[0][0]
            # This case might occur if plain_results was empty or Counter had an issue,
            # though unlikely given the checks.
            # Or if all items are unique and Counter returns multiple items for most_common(1) if counts are 1.
            # Safely return the first result if available, or None.
            return plain_results[0] if plain_results else None

    def run(self, task: str) -> Any:
        """
        Executes a given task by coordinating with teammates.

        The execution logic involves several steps:
        1.  **Attempt Task Decomposition**: Initially, the method calls
            `_try_decompose_task()`. This method now uses an LLM (via a teammate
            with `LLMSkill`) to attempt to break down the input `task` into
            a list of sub-task strings.
        2.  **Sub-Task Execution (if decomposed)**: If `_try_decompose_task()`
            returns a valid list of sub-tasks (even an empty one, which is handled
            by falling through to the 'else' block after a check), and the list is not
            effectively empty (e.g. not `["", ""]`), each sub-task is sequentially
            routed to the most appropriate teammate (using `self.route_task()`).
            The results from these sub-tasks are collected and then aggregated using
            `_aggregate_sub_task_results()`.
        3.  **Standard Execution (if not decomposed or decomposition yields no actionable tasks)**:
            If task decomposition is not attempted (e.g., no LLM skill teammate),
            fails (e.g., LLM error, invalid JSON), or results in no actionable
            sub-tasks (empty list or list of blank strings), the agent processes
            the original task as a single unit. It attempts to route this task to a
            single suitable teammate using `self.route_task()`.
            a.  If a route is found, that teammate executes the task, and its
                result is returned.
            b.  If no specific route is found, the task is broadcast to all
                teammates. Each teammate executes the task, and their individual
                results (or errors) are collected.
        4.  **Result Aggregation (for broadcast)**: The results from a broadcast
            are then aggregated using `self.aggregate_results()` (which may employ
            weighted or majority voting) to produce a final outcome.

        Args:
            task (str): The task description string to be executed.

        Returns:
            Any: The result of the task execution. This could be a combined result
                 from sub-tasks, the direct result from a routed agent, or the
                 aggregated result from multiple agents.
        """
        print(f"[CollaborativeAgent] Received task: {task}")

        sub_tasks = self._try_decompose_task(task)

        # Check if LLM returned a list of sub-tasks, but all are empty or whitespace
        if sub_tasks and not any(st.strip() for st in sub_tasks):
            print(f"[CollaborativeAgent] LLM returned empty or effectively empty sub-tasks. Treating original task as atomic: {task}")
            sub_tasks = None # Force fallback to process original task

        if sub_tasks: # This now correctly handles None from LLM failure, explicit None from above, or a valid list of sub-tasks.
                     # An empty list [] from LLM (meaning "atomic task") will also go to the 'else' block.
            print(f"[CollaborativeAgent] Task decomposed by LLM into {len(sub_tasks)} sub-task(s): {sub_tasks}")
            sub_task_results = []
            for sub_task_string in sub_tasks:
                print(f"[CollaborativeAgent] Processing sub-task: '{sub_task_string}'")
                routed_agent = self.route_task(sub_task_string)
                if routed_agent:
                    print(f"[CollaborativeAgent] Routing sub-task '{sub_task_string}' to agent: {routed_agent.name}")
                    try:
                        result = routed_agent.run(sub_task_string)
                        sub_task_results.append(result)
                        print(f"[CollaborativeAgent] Result for sub-task '{sub_task_string}': {result}")
                    except Exception as e:
                        error_msg = f"Error executing sub-task '{sub_task_string}' by {routed_agent.name}: {e}"
                        print(f"[CollaborativeAgent] {error_msg}")
                        sub_task_results.append(f"[{error_msg}]")
                else:
                    warning_msg = f"No agent found for sub-task: '{sub_task_string}'"
                    print(f"[CollaborativeAgent] [WARNING] {warning_msg}")
                    sub_task_results.append(f"[Sub-task '{sub_task_string}' could not be routed]")

            final_combined_result = self._aggregate_sub_task_results(sub_task_results)
            print(f"[CollaborativeAgent] Final combined result for decomposed task '{task}': {final_combined_result}")
            return final_combined_result
        else:
            # This 'else' block handles:
            # 1. _try_decompose_task returned None (LLM skill not found, LLM error, JSON parse error, or list of blank strings)
            # 2. _try_decompose_task returned [] (LLM deemed task atomic)
            if sub_tasks is None:
                 print(f"[CollaborativeAgent] Task decomposition failed or resulted in blank sub-tasks. Processing as single task: {task}")
            else: # sub_tasks is []
                 print(f"[CollaborativeAgent] LLM deemed task atomic. Processing as single task: {task}")

            # Original logic: Try routing the whole task
            routed_agent = self.route_task(task)
            if routed_agent:
                print(f"[CollaborativeAgent] Routing task '{task}' to agent: {routed_agent.name}")
                result = routed_agent.run(task)
                print(f"[CollaborativeAgent] Result for task '{task}': {result}")
                return result

            # Otherwise, broadcast to all
            print(f"[CollaborativeAgent] No specific route for task '{task}'. Broadcasting to all teammates.")
            results = []
            for agent in self.teammates:
                print(f"[CollaborativeAgent] Delegating task '{task}' to: {agent.name}")
                try:
                    result = agent.run(task)
                    results.append((agent, result))
                except Exception as e:
                    print(f"[CollaborativeAgent] Error during broadcast to {agent.name} for task '{task}': {e}")
                    # Optionally append an error placeholder or skip
                    results.append((agent, f"[Error executing task on {agent.name}]"))

            if not results:
                print(f"[CollaborativeAgent] No results obtained from broadcast for task: {task}")
                return "[No results from any agent]"

            agg = self.aggregate_results(results)
            print(f"[CollaborativeAgent] Aggregated results for task '{task}': {agg}")
            return agg
