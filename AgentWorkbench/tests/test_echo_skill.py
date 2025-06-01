import unittest
from skills import EchoSkill # Ensure this import works based on project structure

class TestEchoSkill(unittest.TestCase):
    def setUp(self):
        self.skill = EchoSkill(name="EchoSkill", description="Echoes input.")

    def test_echo_single_string(self):
        self.assertEqual(self.skill.execute("hello"), "hello")

    def test_echo_empty_string(self):
        self.assertEqual(self.skill.execute(""), "")

    def test_echo_with_numbers(self):
        self.assertEqual(self.skill.execute("12345"), "12345")

    def test_echo_with_special_chars(self):
        self.assertEqual(self.skill.execute("!@#$%^&*()"), "!@#$%^&*()")

    def test_echo_no_args(self):
        self.assertEqual(self.skill.execute(), "") # Assuming it returns empty string for no args

if __name__ == "__main__":
    unittest.main()
