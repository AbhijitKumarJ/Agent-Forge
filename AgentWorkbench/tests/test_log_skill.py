import unittest
import os
import datetime
from unittest.mock import patch, mock_open
from skills import LogSkill # Assuming skills are importable this way from tests

# Define a fixed datetime for consistent timestamps in tests
FIXED_DATETIME = datetime.datetime(2024, 1, 1, 12, 0, 0)

@patch('skills.log_skill.datetime', new_callable=lambda: type('datetime', (), {'datetime': FIXED_DATETIME, 'now': lambda: FIXED_DATETIME}))
class TestLogSkill(unittest.TestCase):

    def setUp(self):
        # Default log file path for most tests
        self.default_log_file = "AgentWorkbench/data/activity.log"
        # Use a different path for specific tests to avoid interference
        self.test_specific_log_file = "AgentWorkbench/data/test_activity.log"

    def tearDown(self):
        # Clean up any created files after tests if necessary,
        # though mocking should prevent most actual file creation.
        # If a test *does* create a real file for some reason, remove it here.
        if os.path.exists(self.test_specific_log_file):
            os.remove(self.test_specific_log_file)
        # It's generally better to avoid creating self.default_log_file in tests
        # and rely entirely on mocks for it.

    @patch('builtins.open', new_callable=mock_open)
    @patch('os.path.exists')
    @patch('os.makedirs')
    def test_log_info_message_success(self, mock_makedirs, mock_exists, mock_file, mock_dt):
        mock_exists.return_value = True # Assume directory exists
        skill = LogSkill(log_file=self.test_specific_log_file)

        result = skill.execute("Test info message", level="INFO")
        self.assertTrue(result)

        expected_log_entry = f"[{FIXED_DATETIME.strftime('%Y-%m-%d %H:%M:%S')}] [INFO] - Test info message\n"
        mock_file.assert_called_once_with(self.test_specific_log_file, "a")
        mock_file().write.assert_called_once_with(expected_log_entry)
        mock_makedirs.assert_not_called() # Dir exists, so makedirs shouldn't be called

    @patch('builtins.open', new_callable=mock_open)
    @patch('os.path.exists')
    @patch('os.makedirs')
    def test_log_warning_message_custom_level(self, mock_makedirs, mock_exists, mock_file, mock_dt):
        mock_exists.return_value = True
        skill = LogSkill(log_file=self.test_specific_log_file)

        result = skill.execute("Test warning message", level="WARNING")
        self.assertTrue(result)

        expected_log_entry = f"[{FIXED_DATETIME.strftime('%Y-%m-%d %H:%M:%S')}] [WARNING] - Test warning message\n"
        mock_file.assert_called_once_with(self.test_specific_log_file, "a")
        mock_file().write.assert_called_once_with(expected_log_entry)

    @patch('builtins.open', new_callable=mock_open)
    @patch('os.path.exists')
    @patch('os.makedirs')
    def test_log_default_level_is_info(self, mock_makedirs, mock_exists, mock_file, mock_dt):
        mock_exists.return_value = True
        skill = LogSkill(log_file=self.test_specific_log_file)

        result = skill.execute("Test default level message") # No level specified
        self.assertTrue(result)

        expected_log_entry = f"[{FIXED_DATETIME.strftime('%Y-%m-%d %H:%M:%S')}] [INFO] - Test default level message\n"
        mock_file().write.assert_called_once_with(expected_log_entry)

    @patch('builtins.open', new_callable=mock_open)
    @patch('os.path.exists')
    @patch('os.makedirs')
    def test_directory_creation_if_not_exists(self, mock_makedirs, mock_exists, mock_file, mock_dt):
        # Simulate directory not existing initially for the first check in __init__
        # then existing for the check in execute (or vice-versa depending on implementation)
        # For LogSkill, _ensure_data_directory is called in __init__ and execute.

        # Scenario: Directory does not exist when __init__ is called
        mock_exists.side_effect = [False, True] # First call (in __init__) False, second (in execute) True

        skill = LogSkill(log_file=self.test_specific_log_file)
        log_dir = os.path.dirname(self.test_specific_log_file)
        mock_makedirs.assert_called_once_with(log_dir) # makedirs called by __init__

        mock_makedirs.reset_mock() # Reset for the call within execute
        mock_exists.side_effect = None # Clear side_effect
        mock_exists.return_value = True # Assume it now exists for the execute call's check

        result = skill.execute("Test message after dir creation")
        self.assertTrue(result)
        mock_makedirs.assert_not_called() # Not called again in execute if dir exists

    @patch('builtins.open', side_effect=IOError("Disk full"))
    @patch('os.path.exists')
    @patch('os.makedirs')
    def test_logging_failure_returns_false(self, mock_makedirs, mock_exists, mock_open_error, mock_dt):
        mock_exists.return_value = True
        skill = LogSkill(log_file=self.test_specific_log_file)

        # We also need to patch print to suppress error messages during test
        with patch('builtins.print') as mock_print:
            result = skill.execute("Test message that will fail")
            self.assertFalse(result)
            mock_print.assert_any_call(f"[{skill.name}] Error logging message 'Test message that will fail': Disk full")

    @patch('os.path.exists')
    @patch('os.makedirs', side_effect=OSError("Permission denied")) # Mock makedirs to fail
    def test_directory_creation_failure_in_init(self, mock_makedirs_fail, mock_exists_fail, mock_dt):
        mock_exists_fail.return_value = False # Directory doesn't exist

        # Patch print to capture the error message during __init__
        with patch('builtins.print') as mock_print:
            skill = LogSkill(log_file=self.test_specific_log_file)
            log_dir = os.path.dirname(self.test_specific_log_file)
            # Verify that the error during makedirs was printed
            mock_print.assert_any_call(f"[{skill.name}] Error creating directory {log_dir}: Permission denied")

        # Even if dir creation fails in init, execute might still try and succeed/fail.
        # Let's test that execute also handles this (though it might be redundant if init raises)
        # For this test, we'll assume init didn't raise and just printed.
        # The execute method will call _ensure_data_directory again.
        mock_exists_fail.return_value = False # Still doesn't exist for the execute call
        mock_makedirs_fail.reset_mock(side_effect=True) # Reset mock for the next call

        with patch('builtins.print') as mock_print_execute, patch('builtins.open', new_callable=mock_open) as mock_file_execute:
            result = skill.execute("Another message")
            # If dir creation fails and skill is designed to not proceed, it should return False
            # or the open call will fail. Given current LogSkill, it would print and then fail at open.
            # If _ensure_data_directory in execute fails to create, open will likely fail.
            # This depends on how robust _ensure_data_directory is.
            # Current LogSkill prints error and continues, so open will be attempted.
            # If the directory truly doesn't exist, open will raise FileNotFoundError.

            # Let's assume the path passed to open is invalid because dir doesn't exist
            mock_file_execute.side_effect = FileNotFoundError("No such file or directory")
            final_result = skill.execute("Message to non-existent dir")
            self.assertFalse(final_result)
            mock_print_execute.assert_any_call(f"[{skill.name}] Error creating directory {log_dir}: Permission denied") # From _ensure_data_directory
            mock_print_execute.assert_any_call(f"[{skill.name}] Error logging message 'Message to non-existent dir': No such file or directory") # From execute's try-except


if __name__ == "__main__":
    unittest.main()
