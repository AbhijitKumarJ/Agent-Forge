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

## Task Decomposition in CollaborativeAgent

### Overview
The `CollaborativeAgent` has a capability to attempt a basic form of task decomposition. This allows it to break down a single, potentially complex task string into multiple simpler sub-tasks. This is an initial step towards more sophisticated task planning and delegation.

### Keyword-Based Decomposition
-   **Mechanism:** The primary method for decomposition is keyword-based. The agent specifically looks for the keyword " and " (with spaces on either side to avoid splitting words like "android").
-   **Behavior:**
    -   The matching is case-insensitive.
    -   Currently, the agent splits the task on the *first detected occurrence* of the keyword " and ". If a task contains multiple " and " keywords, only the first one will be used for splitting, resulting in exactly two sub-tasks. For instance, "task A and task B and task C" becomes `Sub-task 1: "task A"` and `Sub-task 2: "task B and task C"`.
-   **Example:**
    A task like: `"search for latest AI news and summarize key findings"`
    Might be decomposed into:
    *   `Sub-task 1: "search for latest AI news"`
    *   `Sub-task 2: "summarize key findings"`

### Sub-Task Execution
-   **Routing:** Once decomposed, each sub-task is treated as an independent task for the purpose of routing. The `CollaborativeAgent` uses its standard routing logic (checking `capabilities` first, then skill/tool names) to find the most appropriate teammate for each sub-task.
-   **Sequential Execution:** Sub-tasks are currently processed sequentially. The first sub-task is routed and executed, then its result is collected, followed by the second sub-task, and so on.

### Result Aggregation for Sub-Tasks
-   **Method:** After all sub-tasks have been executed (or attempted), their individual results are combined into a single string.
-   **Current Implementation:** The results from each sub-task (including any error messages or placeholders for unroutable sub-tasks) are converted to strings and then joined together, with each sub-task's result appearing on a new line.
-   **Example:**
    If Sub-task 1 (e.g., "search for latest AI news") yields:
    `"AI News Report: AI models are showing unprecedented capabilities..."`
    And Sub-task 2 (e.g., "summarize key findings") yields:
    `"Summary: Key findings indicate AI is advancing rapidly in language understanding and generation."`
    The final combined result returned by the `CollaborativeAgent` would be:
    ```
    AI News Report: AI models are showing unprecedented capabilities...
    Summary: Key findings indicate AI is advancing rapidly in language understanding and generation.
    ```

### Future Enhancements for Decomposition/Aggregation (Conceptual)
While the current keyword-based decomposition is a foundational step, future improvements could involve:
-   **LLM-based Task Decomposition:** Utilizing a Large Language Model to parse and understand more complex task structures, allowing for more nuanced and multi-step decomposition beyond simple keywords.
-   **LLM-based Result Aggregation:** Employing an LLM to synthesize the results from multiple sub-tasks into a more coherent and contextually relevant single response, rather than simple concatenation.

## Extending and Customizing

Developers can leverage these multi-agent features by:

-   Creating `SimpleAgent` instances (or custom agent subclasses) and assigning them specific `capabilities` lists that reflect their expertise.
-   Assigning custom `weight` values to agents to influence their impact on consensus when used within a `CollaborativeAgent`.
-   Designing tasks and prompts that effectively use keywords corresponding to agent capabilities or skill/tool names to enable precise routing.

By clearly defining agent roles through capabilities and weights, and by structuring tasks appropriately, sophisticated collaborative behaviors can be achieved within AgentWorkbench.
```
