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

    def test_subtraction(self):
        self.assertEqual(self.skill.execute("10-5"), 5)

    def test_multiplication(self):
        self.assertEqual(self.skill.execute("3*7"), 21)

    def test_division(self):
        self.assertEqual(self.skill.execute("10/2"), 5)

    def test_division_by_zero(self):
        # The MathSkill currently catches exceptions and returns None
        self.assertIsNone(self.skill.execute("5/0"))

    def test_order_of_operations(self):
        self.assertEqual(self.skill.execute("2+3*4"), 14) # 2 + 12 = 14
        self.assertEqual(self.skill.execute("(2+3)*4"), 20) # 5 * 4 = 20

    def test_negative_numbers(self):
        self.assertEqual(self.skill.execute("-2 + -3"), -5)

    def test_float_numbers(self):
        self.assertEqual(self.skill.execute("1.5 + 2.5"), 4.0)

if __name__ == "__main__":
    unittest.main()
