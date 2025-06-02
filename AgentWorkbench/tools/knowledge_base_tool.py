from core import BaseTool

class KnowledgeBaseTool(BaseTool):
    """A tool that stores and retrieves Q&A pairs in memory (demo knowledge base)."""
    def __init__(self, name, description):
        super().__init__(name, description)
        self.kb = {}

    def use(self, question, answer=None):
        if answer is not None:
            self.kb[question] = answer
            print(f"[KnowledgeBaseTool] Stored: '{question}' -> '{answer}'")
            return True
        result = self.kb.get(question)
        print(f"[KnowledgeBaseTool] Retrieved: '{question}' -> '{result}'")
        return result
