from agents import SimpleAgent, CollaborativeAgent
from skills import EchoSkill, MathSkill, LLMCompletionSkill, WebSearchSkill, WikipediaSkill, TranslationSkill
from tools import PrintTool, ReverseTool, FileTool, SQLiteTool

# 1. MathBot: solves math and prints results
def create_math_bot():
    agent = SimpleAgent(name="MathBot", description="Solves math problems.")
    agent.add_skill(MathSkill(name="MathSkill", description="Evaluates math expressions."))
    agent.add_tool(PrintTool(name="PrintTool", description="Prints output."))
    return agent

# 2. WikiBot: fetches Wikipedia summaries
def create_wiki_bot():
    agent = SimpleAgent(name="WikiBot", description="Fetches Wikipedia summaries.")
    agent.add_skill(WikipediaSkill(name="WikipediaSkill", description="Wikipedia summary."))
    agent.add_tool(PrintTool(name="PrintTool", description="Prints output."))
    return agent

# 3. TranslatorBot: translates text to Spanish
def create_translator_bot():
    agent = SimpleAgent(name="TranslatorBot", description="Translates text to Spanish.")
    agent.add_skill(TranslationSkill(name="TranslationSkill", description="Translates text."))
    agent.add_tool(PrintTool(name="PrintTool", description="Prints output."))
    return agent

# 4. ResearchBot: collaborative agent using WikiBot and MathBot
def create_research_bot():
    wiki_bot = create_wiki_bot()
    math_bot = create_math_bot()
    collab = CollaborativeAgent(name="ResearchBot", description="Researches and calculates.", teammates=[wiki_bot, math_bot])
    return collab

# 5. LLMChatBot: uses LLM for completions
def create_llm_chat_bot():
    agent = SimpleAgent(name="LLMChatBot", description="Chatbot powered by LLM.")
    agent.add_skill(LLMCompletionSkill(name="LLMCompletionSkill", description="LLM completions."))
    agent.add_tool(PrintTool(name="PrintTool", description="Prints output."))
    return agent

# 6. WebSearchBot: uses web search and file saving
def create_web_search_bot():
    agent = SimpleAgent(name="WebSearchBot", description="Searches the web and saves results.")
    agent.add_skill(WebSearchSkill(name="WebSearchSkill", description="Web search."))
    agent.add_tool(FileTool(name="FileTool", description="File I/O."))
    return agent

# 7. ConsensusTeam: 3 agents for consensus demos
def create_consensus_team():
    a1 = create_math_bot()
    a2 = create_wiki_bot()
    a3 = create_translator_bot()
    collab = CollaborativeAgent(name="ConsensusTeam", description="Consensus/voting demo.", teammates=[a1, a2, a3])
    return collab
