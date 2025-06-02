from core import BaseTool

class PrintTool(BaseTool):
    """A tool that prints the input."""

    def use(self, *args, **kwargs):
        print(f"[PrintTool] Print: {args[0] if args else ''}")
