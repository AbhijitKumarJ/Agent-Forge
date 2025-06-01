import unittest
from unittest.mock import patch
import io
from tools import ReverseTool # Assuming tools are importable this way

class TestReverseTool(unittest.TestCase):

    def setUp(self):
        self.tool = ReverseTool(name="TestReverseTool", description="A test reverse tool.")

    @patch('sys.stdout', new_callable=io.StringIO)
    def test_use_reverse_simple_string(self, mock_stdout):
        input_string = "hello"
        expected_reversed = "olleh"
        expected_output_message = f"[ReverseTool] Reversed: {expected_reversed}\n"

        result = self.tool.use(input_string)

        self.assertEqual(result, expected_reversed)
        self.assertEqual(mock_stdout.getvalue(), expected_output_message)

    @patch('sys.stdout', new_callable=io.StringIO)
    def test_use_reverse_string_with_spaces(self, mock_stdout):
        input_string = "hello world"
        expected_reversed = "dlrow olleh"
        expected_output_message = f"[ReverseTool] Reversed: {expected_reversed}\n"

        result = self.tool.use(input_string)

        self.assertEqual(result, expected_reversed)
        self.assertEqual(mock_stdout.getvalue(), expected_output_message)

    @patch('sys.stdout', new_callable=io.StringIO)
    def test_use_reverse_string_with_numbers_and_specials(self, mock_stdout):
        input_string = "123!@# Test"
        expected_reversed = "tseT #@!321"
        expected_output_message = f"[ReverseTool] Reversed: {expected_reversed}\n"

        result = self.tool.use(input_string)

        self.assertEqual(result, expected_reversed)
        self.assertEqual(mock_stdout.getvalue(), expected_output_message)

    @patch('sys.stdout', new_callable=io.StringIO)
    def test_use_reverse_empty_string(self, mock_stdout):
        input_string = ""
        expected_reversed = ""
        expected_output_message = f"[ReverseTool] Reversed: {expected_reversed}\n"

        result = self.tool.use(input_string)

        self.assertEqual(result, expected_reversed)
        self.assertEqual(mock_stdout.getvalue(), expected_output_message)

    @patch('sys.stdout', new_callable=io.StringIO)
    def test_use_no_arguments(self, mock_stdout):
        expected_reversed = "" # Defaults to empty string
        expected_output_message = f"[ReverseTool] Reversed: {expected_reversed}\n"

        result = self.tool.use()

        self.assertEqual(result, expected_reversed)
        self.assertEqual(mock_stdout.getvalue(), expected_output_message)

    @patch('sys.stdout', new_callable=io.StringIO)
    def test_use_reverse_palindrome(self, mock_stdout):
        input_string = "madam"
        expected_reversed = "madam"
        expected_output_message = f"[ReverseTool] Reversed: {expected_reversed}\n"

        result = self.tool.use(input_string)

        self.assertEqual(result, expected_reversed)
        self.assertEqual(mock_stdout.getvalue(), expected_output_message)

    @patch('sys.stdout', new_callable=io.StringIO)
    def test_use_with_multiple_arguments(self, mock_stdout):
        # ReverseTool only considers the first argument
        input_string1 = "first"
        input_string2 = "second"
        expected_reversed = "tsrif"
        expected_output_message = f"[ReverseTool] Reversed: {expected_reversed}\n"

        result = self.tool.use(input_string1, input_string2)

        self.assertEqual(result, expected_reversed)
        self.assertEqual(mock_stdout.getvalue(), expected_output_message)

    def test_use_with_non_string_input_integer(self):
        # The tool currently doesn't handle non-string types gracefully for slicing
        # and will raise an AttributeError or TypeError if s[::-1] is used on an int.
        # Since ReverseTool has no try-except, the error should propagate.
        with self.assertRaises(TypeError): # Corrected to TypeError as per s[::-1] on int
            self.tool.use(123)

    def test_use_with_non_string_input_list(self):
        # A list can be sliced, so this should "work" but might not be intended.
        # The tool's description says "reverses the input string".
        # This test clarifies its behavior with list inputs.
        input_list = [1, 2, 3]
        expected_reversed_list = [3, 2, 1]

        # We don't check stdout here as the print formatting might be weird for lists,
        # or we might decide the tool should explicitly only handle strings.
        # For now, just testing the return value.
        # If strict string-only behavior is desired, the tool should be modified.
        with patch('sys.stdout', new_callable=io.StringIO): # Still mock stdout to suppress print
            result = self.tool.use(input_list)
            self.assertEqual(result, expected_reversed_list)

if __name__ == "__main__":
    unittest.main()
