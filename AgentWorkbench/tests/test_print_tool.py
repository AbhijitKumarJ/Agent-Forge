import unittest
from unittest.mock import patch
import io # For capturing print output
from tools import PrintTool # Assuming tools are importable this way

class TestPrintTool(unittest.TestCase):

    def setUp(self):
        self.tool = PrintTool(name="TestPrintTool", description="A test print tool.")

    @patch('sys.stdout', new_callable=io.StringIO)
    def test_use_with_single_argument(self, mock_stdout):
        input_text = "Hello, Agent!"
        expected_output = f"[PrintTool] Print: {input_text}\n"

        self.tool.use(input_text)

        self.assertEqual(mock_stdout.getvalue(), expected_output)

    @patch('sys.stdout', new_callable=io.StringIO)
    def test_use_with_multiple_arguments(self, mock_stdout):
        input_text1 = "FirstArgument"
        input_text2 = "SecondArgument"
        expected_output = f"[PrintTool] Print: {input_text1}\n" # Only first arg is used

        self.tool.use(input_text1, input_text2)

        self.assertEqual(mock_stdout.getvalue(), expected_output)

    @patch('sys.stdout', new_callable=io.StringIO)
    def test_use_with_no_arguments(self, mock_stdout):
        expected_output = "[PrintTool] Print: \n" # Empty string after prefix

        self.tool.use()

        self.assertEqual(mock_stdout.getvalue(), expected_output)

    @patch('sys.stdout', new_callable=io.StringIO)
    def test_use_with_empty_string_argument(self, mock_stdout):
        input_text = ""
        expected_output = f"[PrintTool] Print: {input_text}\n"

        self.tool.use(input_text)

        self.assertEqual(mock_stdout.getvalue(), expected_output)

    @patch('sys.stdout', new_callable=io.StringIO)
    def test_use_with_numbers_and_special_chars(self, mock_stdout):
        input_text = "123 !@#$%^&*()-_=+"
        expected_output = f"[PrintTool] Print: {input_text}\n"

        self.tool.use(input_text)

        self.assertEqual(mock_stdout.getvalue(), expected_output)

if __name__ == "__main__":
    unittest.main()
