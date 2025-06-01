import unittest
from unittest.mock import patch, mock_open
from tools import FileTool # Assuming tools are importable this way

class TestFileTool(unittest.TestCase):

    def setUp(self):
        self.tool = FileTool(name="TestFileTool", description="A test file tool.")
        self.test_filepath = "dummy/path/to/test_file.txt"

    @patch('builtins.open', new_callable=mock_open, read_data="Test content")
    @patch('builtins.print') # To suppress and optionally check print statements
    def test_use_read_mode_success(self, mock_print, mock_file):
        expected_content = "Test content"

        # Call the tool's use method in read mode
        result = self.tool.use(filepath=self.test_filepath, mode='r')

        # Assertions
        mock_file.assert_called_once_with(self.test_filepath, 'r')
        self.assertEqual(result, expected_content)
        mock_print.assert_any_call(f"[FileTool] Read from {self.test_filepath}: {expected_content}")

    @patch('builtins.open', new_callable=mock_open)
    @patch('builtins.print')
    def test_use_write_mode_success(self, mock_print, mock_file):
        content_to_write = "Hello, world!"

        # Call the tool's use method in write mode
        result = self.tool.use(filepath=self.test_filepath, content=content_to_write, mode='w')

        # Assertions
        mock_file.assert_called_once_with(self.test_filepath, 'w')
        mock_file().write.assert_called_once_with(content_to_write)
        self.assertTrue(result)
        mock_print.assert_any_call(f"[FileTool] Wrote to {self.test_filepath}: {content_to_write}")

    @patch('builtins.print')
    def test_use_write_mode_missing_content(self, mock_print):
        # Call the tool's use method in write mode but without content
        result = self.tool.use(filepath=self.test_filepath, mode='w') # content is None by default

        # Assertions
        self.assertFalse(result)
        mock_print.assert_any_call("[FileTool] Invalid mode or missing content.")

    @patch('builtins.print')
    def test_use_invalid_mode(self, mock_print):
        # Call the tool's use method with an unsupported mode
        result = self.tool.use(filepath=self.test_filepath, mode='a') # 'a' for append is not supported

        # Assertions
        self.assertFalse(result)
        mock_print.assert_any_call("[FileTool] Invalid mode or missing content.")

    @patch('builtins.open', side_effect=FileNotFoundError("[Errno 2] No such file or directory: 'dummy/path/to/test_file.txt'"))
    @patch('builtins.print')
    def test_use_read_mode_file_not_found(self, mock_print, mock_open_error):
        # Call the tool's use method in read mode when file doesn't exist
        result = self.tool.use(filepath=self.test_filepath, mode='r')

        # Assertions
        self.assertIsNone(result)
        mock_open_error.assert_called_once_with(self.test_filepath, 'r')
        # The actual error message from FileNotFoundError includes more details,
        # so we check for the generic part FileTool prints.
        mock_print.assert_any_call(f"[FileTool] Error: [Errno 2] No such file or directory: '{self.test_filepath}'")


    @patch('builtins.open', side_effect=IOError("Permission denied"))
    @patch('builtins.print')
    def test_use_write_mode_permission_error(self, mock_print, mock_open_error):
        content_to_write = "Cannot write this."

        # Call the tool's use method in write mode when permission is denied
        result = self.tool.use(filepath=self.test_filepath, content=content_to_write, mode='w')

        # Assertions
        self.assertIsNone(result)
        mock_open_error.assert_called_once_with(self.test_filepath, 'w')
        mock_print.assert_any_call(f"[FileTool] Error: Permission denied")

    @patch('builtins.open', new_callable=mock_open)
    @patch('builtins.print')
    def test_use_read_mode_empty_file(self, mock_print, mock_file):
        mock_file.return_value.read.return_value = "" # Configure mock for open().read()

        result = self.tool.use(filepath=self.test_filepath, mode='r')

        self.assertEqual(result, "")
        mock_file.assert_called_once_with(self.test_filepath, 'r')
        mock_print.assert_any_call(f"[FileTool] Read from {self.test_filepath}: ")

if __name__ == "__main__":
    unittest.main()
