import streamlit as st
from agents import SimpleAgent, CollaborativeAgent
from skills import EchoSkill, MathSkill, LLMSkill, WebSearchSkill, WebScrapeSkill
from tools import PrintTool, ReverseTool, FileTool, KnowledgeBaseTool, SQLiteTool

st.title("Agent Workbench UI (Advanced)")

agent_types = ["SimpleAgent", "CollaborativeAgent"]
agent_type = st.selectbox("Choose agent type", agent_types)
task = st.text_input("Enter a task or query", "2+2")

skill_options = ["EchoSkill", "MathSkill", "LLMSkill", "WebSearchSkill", "WebScrapeSkill", "WeatherSkill", "FinanceSkill", "NewsSkill", "WikipediaSkill", "TranslationSkill"]
tool_options = ["PrintTool", "ReverseTool", "FileTool", "KnowledgeBaseTool", "SQLiteTool"]

if agent_type == "SimpleAgent":
    agent = SimpleAgent(name="UIAgent", description="Agent via Streamlit UI.")
    skill = st.selectbox("Skill", skill_options)
    tool = st.selectbox("Tool", tool_options)
    # Assign skill
    if skill == "EchoSkill":
        agent.add_skill(EchoSkill(name="EchoSkill", description="Echoes input."))
    elif skill == "MathSkill":
        agent.add_skill(MathSkill(name="MathSkill", description="Evaluates math."))
    elif skill == "LLMSkill":
        agent.add_skill(LLMSkill(name="LLMSkill", description="LLM API call."))
    elif skill == "WebSearchSkill":
        agent.add_skill(WebSearchSkill(name="WebSearchSkill", description="Web search."))
    elif skill == "WebScrapeSkill":
        agent.add_skill(WebScrapeSkill(name="WebScrapeSkill", description="Web scraping."))
    # Assign tool
    if tool == "PrintTool":
        agent.add_tool(PrintTool(name="PrintTool", description="Prints input."))
    elif tool == "ReverseTool":
        agent.add_tool(ReverseTool(name="ReverseTool", description="Reverses input."))
    elif tool == "FileTool":
        agent.add_tool(FileTool(name="FileTool", description="File I/O."))
    elif tool == "KnowledgeBaseTool":
        agent.add_tool(KnowledgeBaseTool(name="KnowledgeBaseTool", description="In-memory Q&A KB."))
    elif tool == "SQLiteTool":
        agent.add_tool(SQLiteTool(name="SQLiteTool", description="Persistent SQLite DB."))
    if st.button("Run Agent"):
        agent.run(task)

elif agent_type == "CollaborativeAgent":
    st.write("Configure teammates for the collaborative agent (up to 5):")
    num_teammates = st.slider("Number of teammates", 2, 5, 3)
    teammates = []
    teammate_results = []
    for i in range(num_teammates):
        skill = st.selectbox(f"Teammate {i+1} Skill", skill_options, key=f"tm{i+1}_skill")
        tool = st.selectbox(f"Teammate {i+1} Tool", tool_options, key=f"tm{i+1}_tool")
        agent = SimpleAgent(name=f"Agent{i+1}", description=f"Teammate {i+1}")
        # Assign skill
        if skill == "EchoSkill":
            agent.add_skill(EchoSkill(name="EchoSkill", description="Echoes input."))
        elif skill == "MathSkill":
            agent.add_skill(MathSkill(name="MathSkill", description="Evaluates math."))
        elif skill == "LLMSkill":
            agent.add_skill(LLMSkill(name="LLMSkill", description="LLM API call."))
        elif skill == "WebSearchSkill":
            agent.add_skill(WebSearchSkill(name="WebSearchSkill", description="Web search."))
        elif skill == "WebScrapeSkill":
            agent.add_skill(WebScrapeSkill(name="WebScrapeSkill", description="Web scraping."))
        elif skill == "WeatherSkill":
            from skills import WeatherSkill
            agent.add_skill(WeatherSkill(name="WeatherSkill", description="Weather API."))
        elif skill == "FinanceSkill":
            from skills import FinanceSkill
            agent.add_skill(FinanceSkill(name="FinanceSkill", description="Finance API."))
        elif skill == "NewsSkill":
            from skills import NewsSkill
            agent.add_skill(NewsSkill(name="NewsSkill", description="News API."))
        # Assign tool
        if tool == "PrintTool":
            agent.add_tool(PrintTool(name="PrintTool", description="Prints input."))
        elif tool == "ReverseTool":
            agent.add_tool(ReverseTool(name="ReverseTool", description="Reverses input."))
        elif tool == "FileTool":
            agent.add_tool(FileTool(name="FileTool", description="File I/O."))
        elif tool == "KnowledgeBaseTool":
            agent.add_tool(KnowledgeBaseTool(name="KnowledgeBaseTool", description="In-memory Q&A KB."))
        elif tool == "SQLiteTool":
            agent.add_tool(SQLiteTool(name="SQLiteTool", description="Persistent SQLite DB."))
        teammates.append(agent)
    collab = CollaborativeAgent(name="Coordinator", description="Delegates, negotiates, consensus.", teammates=teammates)
    if st.button("Run Collaborative Agent"):
        # Patch collab.run to collect all teammate results for visualization
        results = []
        for agent in teammates:
            try:
                res = agent.run(task)
            except Exception as e:
                res = f"Error: {e}"
            results.append((agent.name, res))
        from collections import Counter
        agg = Counter([r for _, r in results])
        consensus = agg.most_common(1)[0][0] if agg else None
        st.write("### Protocol Results Breakdown:")
        for name, res in results:
            st.write(f"{name}: {res}")
        st.write(f"**Consensus/Voting Result:** {consensus}")

st.write("---")
st.write("You can extend this UI to add more agent types, skills, tools, and advanced multi-agent protocols!")
