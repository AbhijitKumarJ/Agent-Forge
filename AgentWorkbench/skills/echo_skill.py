from core import BaseSkill

class EchoSkill(BaseSkill):
    """A skill that simply echoes the input."""

    def execute(self, *args, **kwargs):
        print(f"[EchoSkill] Echo: {args[0] if args else ''}")
