import unittest
from unittest.mock import patch, MagicMock, mock_open
import os # For os.path.exists
# The tool is named SQLiteTool in the file, not DBTool
from tools import SQLiteTool

class TestSQLiteTool(unittest.TestCase):

    def setUp(self):
        self.db_path = "test_agentworkbench.db"
        # We will patch 'sqlite3.connect' and 'os.path.exists'
        # The tool instance will be created within each test method
        # after mocks are set up, to ensure it uses the mocked versions.

    # Test _ensure_db method indirectly by testing __init__
    @patch('tools.db_tool.sqlite3.connect') # Path to sqlite3 where it's used by SQLiteTool
    @patch('tools.db_tool.os.path.exists')
    def test_init_db_creation_if_not_exists(self, mock_path_exists, mock_sqlite_connect):
        mock_path_exists.return_value = False # Simulate DB does not exist
        mock_conn = MagicMock()
        mock_sqlite_connect.return_value.__enter__.return_value = mock_conn # Mock context manager

        tool = SQLiteTool(name="TestDB", description="Test DB Tool", db_path=self.db_path)

        mock_path_exists.assert_called_once_with(self.db_path)
        mock_sqlite_connect.assert_called_once_with(self.db_path)
        mock_conn.execute.assert_called_once_with('CREATE TABLE IF NOT EXISTS kv (key TEXT PRIMARY KEY, value TEXT)')
        self.assertEqual(tool.db_path, self.db_path)

    @patch('tools.db_tool.sqlite3.connect')
    @patch('tools.db_tool.os.path.exists')
    def test_init_db_exists(self, mock_path_exists, mock_sqlite_connect):
        mock_path_exists.return_value = True # Simulate DB exists

        tool = SQLiteTool(name="TestDB", description="Test DB Tool", db_path=self.db_path)

        mock_path_exists.assert_called_once_with(self.db_path)
        mock_sqlite_connect.assert_not_called() # connect shouldn't be called by _ensure_db if file exists
        # Note: _ensure_db only connects if db file !exist. The use() method will connect regardless.

    @patch('tools.db_tool.sqlite3.connect')
    @patch('builtins.print') # To capture print statements
    def test_use_store_value_success(self, mock_print, mock_sqlite_connect):
        mock_conn = MagicMock()
        mock_sqlite_connect.return_value.__enter__.return_value = mock_conn

        # Instantiate tool AFTER mocks are set up if its __init__ uses them.
        # In this case, __init__ uses os.path.exists, so we need to ensure that's handled
        # if we were testing __init__'s db creation part here too.
        # For simplicity, assume _ensure_db is tested separately or os.path.exists allows it.
        with patch('tools.db_tool.os.path.exists', return_value=True): # Assume DB file exists for this test
            tool = SQLiteTool(name="TestDB", description="Test DB Tool", db_path=self.db_path)

        key, value = "test_key", "test_value"
        result = tool.use(key, value=value)

        self.assertTrue(result)
        mock_sqlite_connect.assert_called_once_with(self.db_path)
        mock_conn.execute.assert_called_once_with('REPLACE INTO kv (key, value) VALUES (?, ?)', (key, value))
        mock_print.assert_any_call(f"[SQLiteTool] Stored: {key} -> {value}")

    @patch('tools.db_tool.sqlite3.connect')
    @patch('builtins.print')
    def test_use_retrieve_value_success(self, mock_print, mock_sqlite_connect):
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = ("retrieved_value",) # Note: fetchone returns a tuple

        mock_conn = MagicMock()
        mock_conn.execute.return_value = mock_cursor
        mock_sqlite_connect.return_value.__enter__.return_value = mock_conn

        with patch('tools.db_tool.os.path.exists', return_value=True):
            tool = SQLiteTool(name="TestDB", description="Test DB Tool", db_path=self.db_path)

        key = "test_key"
        expected_value = "retrieved_value"
        result = tool.use(key) # Value is None, so retrieve

        self.assertEqual(result, expected_value)
        mock_sqlite_connect.assert_called_once_with(self.db_path)
        mock_conn.execute.assert_called_once_with('SELECT value FROM kv WHERE key=?', (key,))
        mock_cursor.fetchone.assert_called_once()
        mock_print.assert_any_call(f"[SQLiteTool] Retrieved: {key} -> {expected_value}")

    @patch('tools.db_tool.sqlite3.connect')
    @patch('builtins.print')
    def test_use_retrieve_value_not_found(self, mock_print, mock_sqlite_connect):
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = None # Simulate key not found

        mock_conn = MagicMock()
        mock_conn.execute.return_value = mock_cursor
        mock_sqlite_connect.return_value.__enter__.return_value = mock_conn

        with patch('tools.db_tool.os.path.exists', return_value=True):
            tool = SQLiteTool(name="TestDB", description="Test DB Tool", db_path=self.db_path)

        key = "non_existent_key"
        result = tool.use(key)

        self.assertIsNone(result)
        mock_print.assert_any_call(f"[SQLiteTool] Retrieved: {key} -> None")

    @patch('tools.db_tool.sqlite3.connect', side_effect=Exception("DB connection error"))
    @patch('builtins.print')
    def test_use_general_exception_handling(self, mock_print, mock_sqlite_connect_error):
        # This will mock the connect call itself to throw an error
        with patch('tools.db_tool.os.path.exists', return_value=True):
            tool = SQLiteTool(name="TestDB", description="Test DB Tool", db_path=self.db_path)

        key, value = "test_key", "test_value"
        result = tool.use(key, value=value)

        self.assertIsNone(result)
        mock_print.assert_any_call(f"[SQLiteTool] Error: DB connection error")

    @patch('tools.db_tool.sqlite3.connect')
    @patch('builtins.print')
    def test_use_execute_exception_handling(self, mock_print, mock_sqlite_connect):
        # Mock execute() to raise an error
        mock_conn = MagicMock()
        mock_conn.execute.side_effect = Exception("SQL execution error")
        mock_sqlite_connect.return_value.__enter__.return_value = mock_conn

        with patch('tools.db_tool.os.path.exists', return_value=True):
            tool = SQLiteTool(name="TestDB", description="Test DB Tool", db_path=self.db_path)

        key, value = "test_key_fail", "test_value_fail"
        result = tool.use(key, value=value)

        self.assertIsNone(result)
        mock_print.assert_any_call(f"[SQLiteTool] Error: SQL execution error")


if __name__ == "__main__":
    unittest.main()
