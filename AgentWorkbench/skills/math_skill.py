from core import BaseSkill

class MathSkill(BaseSkill):
    """A skill that evaluates simple math expressions from a string."""
    def execute(self, *args, **kwargs):
        expr = args[0] if args else ''
        try:
            result = eval(expr, {"__builtins__": {}})
            print(f"[MathSkill] Result: {result}")
            return result
        except Exception as e:
            print(f"[MathSkill] Error evaluating '{expr}': {e}")
            return None
