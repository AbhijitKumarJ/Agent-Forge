import unittest
from skills import MathSkill

class TestMathSkill(unittest.TestCase):
    def setUp(self):
        self.skill = MathSkill(name="MathSkill", description="Evaluates math expressions.")

    def test_addition(self):
        result = self.skill.execute("2+2")
        self.assertEqual(result, 4)

    def test_invalid_expression(self):
        result = self.skill.execute("2+unknown")
        self.assertIsNone(result)

if __name__ == "__main__":
    unittest.main()
