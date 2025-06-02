from core import BaseSkill

class EchoSkill(BaseSkill):
    """A skill that simply echoes the input."""

    def execute(self, *args, **kwargs):
        echo_str = args[0] if args else ""
        print(f"[EchoSkill] Echo: {echo_str}")
        return echo_str
