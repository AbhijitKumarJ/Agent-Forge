# Main entry point for the Agent Workbench
import argparse
from config import LOG_LEVEL
from agents import SimpleAgent, CollaborativeAgent
from skills import EchoSkill, MathSkill, LLMSkill
from tools import PrintTool, ReverseTool


def main():
    parser = argparse.ArgumentParser(description="Agent Workbench CLI")
    parser.add_argument('--task', type=str, help='Task for the agent', default="Say hello!")
    parser.add_argument('--multi', action='store_true', help='Run multi-agent demo')
    parser.add_argument('--llm', action='store_true', help='Use LLMCompletionSkill demo')
    args = parser.parse_args()

    print(f"[Workbench] LOG_LEVEL: {LOG_LEVEL}")
    print("Initializing Agent Workbench...")

    if args.multi:
        # Multi-agent demo: two SimpleAgents coordinated by a CollaborativeAgent
        agent1 = SimpleAgent(name="Agent1", description="Handles echoing.")
        agent1.add_skill(EchoSkill(name="EchoSkill", description="Echoes input."))
        agent1.add_tool(PrintTool(name="PrintTool", description="Prints input."))

        agent2 = SimpleAgent(name="Agent2", description="Handles math and reverse.")
        agent2.add_skill(MathSkill(name="MathSkill", description="Evaluates math expressions."))
        agent2.add_tool(ReverseTool(name="ReverseTool", description="Reverses input."))

        collab = CollaborativeAgent(name="Coordinator", description="Delegates to teammates.", teammates=[agent1, agent2])
        collab.run(args.task)
        print("Multi-agent demo complete.")
    elif args.llm:
        # LLM API demo (requires openai and API key)
        agent = SimpleAgent(name="LLMAgent", description="Agent with LLM skill.")
        llm_skill = LLMSkill(name="LLMSkill", description="Calls OpenAI API.")
        agent.add_skill(llm_skill)
        agent.run(args.task)
        print("LLM API demo complete.")
    else:
        # Single agent demo
        agent = SimpleAgent(name="DemoAgent", description="A simple demonstration agent.")
        echo_skill = EchoSkill(name="EchoSkill", description="Echoes the input.")
        print_tool = PrintTool(name="PrintTool", description="Prints the input.")
        agent.add_skill(echo_skill)
        agent.add_tool(print_tool)
        agent.run(args.task)
        print("Agent Workbench demo complete.")

if __name__ == "__main__":
    main()
