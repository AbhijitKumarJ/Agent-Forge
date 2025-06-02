# Multi-Agent Systems in AgentWorkbench

## Introduction

Multi-agent collaboration in AgentWorkbench allows for the creation of more sophisticated and specialized AI systems. By combining multiple agents, each potentially with unique skills, tools, or designated capabilities, complex tasks can be broken down, delegated, and results can be aggregated to form a cohesive response. This approach enables building systems that are more robust, flexible, and capable than a single monolithic agent.

## Core Component: `CollaborativeAgent`

The central piece for multi-agent systems in AgentWorkbench is the `CollaborativeAgent`. It acts as a coordinator or a manager for a team of other agents (referred to as "teammates").

-   **Role:** The `CollaborativeAgent` is responsible for receiving tasks, deciding how to handle them (either by routing to a specific teammate or broadcasting to all), and then aggregating the results from its teammates to produce a final outcome.
-   **Adding Teammates:** Teammates (which are instances of `BaseAgent` or its subclasses like `SimpleAgent`) are typically provided during the initialization of the `CollaborativeAgent` or can be added using its `add_teammate` method.

## Task Routing

`CollaborativeAgent.route_task` implements a specific strategy to determine the most appropriate teammate for a given task:

1.  **Primary Routing via `capabilities`:**
    *   Agents derived from `BaseAgent` can be initialized with a `capabilities` attribute, which is a list of strings defining their specializations (e.g., `["search", "data analysis", "image generation"]`).
    *   When a task is received, `CollaborativeAgent` first iterates through its teammates. It checks if any keyword from a teammate's `capabilities` list is present (case-insensitive) in the task description string.
    *   The first teammate found with a matching capability is selected to handle the task.

2.  **Fallback to Skill/Tool Name Matching:**
    *   If no teammate is identified based on `capabilities`, the `CollaborativeAgent` falls back to a secondary matching strategy.
    *   It again iterates through the teammates, this time checking if any of their attached skill names or tool names (case-insensitive) are present as keywords in the task description string.
    *   The first teammate found with a matching skill or tool name is selected.

3.  **Broadcast (No Match):**
    *   If neither capabilities nor skill/tool names lead to a specific teammate, the task is typically broadcast to all teammates (this is handled in the `run` method of `CollaborativeAgent` if `route_task` returns `None`).

**Conceptual Routing Logic:**

```plaintext
Function route_task(task_description, teammates):
  // Stage 1: Match by Capabilities
  For each agent in teammates:
    If agent has 'capabilities':
      For each capability_keyword in agent.capabilities:
        If capability_keyword is in task_description:
          Return agent // Route to this agent

  // Stage 2: Match by Skill/Tool Names
  For each agent in teammates:
    For each skill_name in agent.skills:
      If skill_name is in task_description:
        Return agent // Route to this agent
    For each tool_name in agent.tools:
      If tool_name is in task_description:
        Return agent // Route to this agent

  Return None // No specific agent found for routing
```

**Example:**

```python
# (Conceptual Python-like example, actual API may vary slightly)

# Agent A definition with capabilities
agent_A = SimpleAgent(name="SearchExpert", description="Finds info online",
                      capabilities=["search", "news lookup"])
agent_A.add_skill(WebSearchSkill(name="WebSearch")) # Also has a skill

# Agent B definition with a specific skill
agent_B = SimpleAgent(name="CalcBot", description="Performs calculations")
agent_B.add_skill(MathSkill(name="MathSkill"))

# Collaborative Agent
coordinator = CollaborativeAgent(
    name="MainCoordinator",
    description="Manages SearchExpert and CalcBot",
    teammates=[agent_A, agent_B]
)

# Task 1: Routed to Agent A based on "search" capability
coordinator.run("search for today's weather")

# Task 2: Routed to Agent B based on "MathSkill" name (fallback)
coordinator.run("calculate value of MathSkill expression 2+2")

# Task 3: Potentially routed to Agent A if "WebSearch" skill name matches
coordinator.run("Use WebSearch for latest articles")
```

## Consensus Mechanisms

When a task is broadcast to multiple teammates, or when results from different routes need reconciliation, the `CollaborativeAgent.aggregate_results` method is invoked. It determines a final outcome based on the responses from teammates:

-   **Weighted Voting:**
    *   Each agent (derived from `BaseAgent`) has a `weight` attribute, which defaults to `1.0`. This weight can be customized during agent initialization.
    *   If all teammates providing results have a valid numerical weight, `aggregate_results` performs weighted voting. The result proposed by an agent is multiplied by its weight, and the result with the highest total weighted score is chosen as the final answer.
    *   This allows for scenarios where certain agents are considered more reliable or authoritative, and their opinions are given more significance.

-   **Majority Vote (Fallback):**
    *   If any of the teammates involved in providing results do not have a valid `weight` attribute (e.g., it's `None`), the system automatically falls back to a simple majority vote.
    *   In this mode, each agent's result counts as one vote, and the result that receives the most votes is chosen. `collections.Counter` is typically used for this.

-   **Handling Non-Hashable Results:** The aggregation logic attempts to handle non-hashable results (like lists or dictionaries) by converting them to hashable equivalents (e.g., tuples) before tallying scores in weighted voting.

**Example:**

```plaintext
# Scenario 1: Weighted Voting
# Agent X (weight 2.0) suggests "Action Alpha"
# Agent Y (weight 1.0) suggests "Action Beta"
# Agent Z (weight 1.0) suggests "Action Beta"
# Weighted scores: "Action Alpha" = 2.0, "Action Beta" = 1.0 + 1.0 = 2.0
# Result: "Action Alpha" (or "Action Beta" - depends on tie-breaking, often the first one encountered with max score)

# Scenario 2: Majority Vote (e.g., Agent Y's weight was None)
# Agent P (weight 1.0 or default) suggests "Proceed"
# Agent Q (weight None) suggests "Wait"
# Agent R (weight 1.0 or default) suggests "Proceed"
# Votes: "Proceed" = 2, "Wait" = 1
# Result: "Proceed"
```

## LLM-Based Task Decomposition in `CollaborativeAgent`

### Overview
The `CollaborativeAgent` now leverages Large Language Models (LLMs) for more sophisticated task decomposition. Instead of relying on simple keyword splitting, it can analyze complex tasks and break them down into a series of more granular, actionable sub-tasks. This enhances the agent's ability to plan and delegate work effectively within its team.

### Mechanism
1.  **Locating LLMSkill:** When a task is received, the `CollaborativeAgent` first searches among its teammates for an agent that possesses an `LLMSkill`.
2.  **Prompting the LLM:** If an `LLMSkill`-equipped teammate is found, a specialized prompt is constructed. This prompt instructs the LLM to act as a task decomposition assistant, analyze the user's task, and return a list of sub-tasks in JSON format.
3.  **Processing LLM Response:** The `CollaborativeAgent` expects the LLM to output a JSON array of strings, where each string is a distinct sub-task.
4.  **Fallback:** If no teammate has an `LLMSkill`, or if the LLM call fails (e.g., API error, network issue), or if the LLM's response cannot be successfully parsed as a JSON list of strings, the `CollaborativeAgent` will fall back to treating the original task as a single, non-decomposed unit. It will then attempt to route this original task using its standard routing logic.

### LLM Output and Atomic Tasks
-   **Expected Format:** The system strictly expects a JSON-formatted list of strings from the LLM (e.g., `["sub-task one", "sub-task two"]`).
-   **Atomic Tasks:** If the LLM determines that a given task is already simple enough and does not require decomposition, it is instructed to return an empty JSON list (`[]`). When the `CollaborativeAgent` receives an empty list, it understands that the original task should be treated as atomic and proceeds to route or broadcast it as a whole. Similarly, if the LLM returns a list containing only empty or whitespace strings, this is also treated as an indication that no actionable sub-tasks were generated, and the original task is processed.

### Example of LLM-Driven Decomposition
Consider the following complex task:
`Task: "Plan a weekend trip to San Francisco for next month, including finding flights, booking a pet-friendly hotel, and listing three activities."`

A capable LLM, when prompted correctly, might decompose this into:
```json
[
    "Find flight options to San Francisco for next month",
    "Research and identify pet-friendly hotel options in San Francisco for the chosen dates",
    "List three potential activities or points of interest in San Francisco suitable for a weekend trip"
]
```

### Sub-Task Execution
-   **Routing:** Once successfully decomposed by the LLM, each sub-task string is treated as an independent task. The `CollaborativeAgent` uses its standard routing logic (checking `capabilities` first, then skill/tool names) to find the most appropriate teammate for *each individual sub-task*.
-   **Sequential Execution:** Sub-tasks are currently processed sequentially. The first sub-task from the LLM's list is routed and executed, its result collected, then the second sub-task, and so on.

### Result Aggregation for Sub-Tasks
-   **Method:** After all generated sub-tasks have been executed (or an attempt has been made), their individual results are combined.
-   **Current Implementation:** The results from each sub-task (which can include actual outcomes, error messages, or placeholders for unroutable sub-tasks) are converted to strings and then joined together, with each sub-task's result appearing on a new line.
-   **Example (following the trip planning task):**
    If the sub-tasks yielded:
    1.  `"Flight options: SFO Air, United..."`
    2.  `"Pet-friendly hotels: Hotel PAWsome, The Canine Courtyard..."`
    3.  `"Activities: Golden Gate Bridge, Alcatraz, Fisherman's Wharf."`

    The final combined result would be:
    ```
    Flight options: SFO Air, United...
    Pet-friendly hotels: Hotel PAWsome, The Canine Courtyard...
    Activities: Golden Gate Bridge, Alcatraz, Fisherman's Wharf.
    ```

### Future Enhancements for Decomposition/Aggregation
While the current LLM-based decomposition significantly improves upon keyword methods, further advancements could include:
-   **More Complex Decomposition Logics:** Utilizing LLMs for more advanced reasoning, such as identifying dependencies between sub-tasks or creating conditional execution paths.
-   **Sophisticated Result Synthesis:** Employing an LLM to synthesize the results from multiple sub-tasks into a more coherent, contextually integrated, and human-readable final narrative, rather than simple string concatenation.

## Extending and Customizing

Developers can leverage these multi-agent features by:

-   Creating `SimpleAgent` instances (or custom agent subclasses) and assigning them specific `capabilities` lists that reflect their expertise.
-   Assigning custom `weight` values to agents to influence their impact on consensus when used within a `CollaborativeAgent`.
-   Designing tasks and prompts that effectively use keywords corresponding to agent capabilities or skill/tool names to enable precise routing.

By clearly defining agent roles through capabilities and weights, and by structuring tasks appropriately, sophisticated collaborative behaviors can be achieved within AgentWorkbench.
```
