from core import BaseTool

class ReverseTool(BaseTool):
    """A tool that reverses the input string."""
    def use(self, *args, **kwargs):
        s = args[0] if args else ''
        reversed_s = s[::-1]
        print(f"[ReverseTool] Reversed: {reversed_s}")
        return reversed_s
