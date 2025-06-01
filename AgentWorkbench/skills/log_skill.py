import os
import datetime
from core import BaseSkill
from config import settings

class LogSkill(BaseSkill):
    """A skill to log messages to a file."""

    def __init__(self, name="LogSkill", description="Logs messages to a file.", log_file=None):
        super().__init__(name, description)
        if log_file is None:
            self.log_file_path = settings.DEFAULT_LOG_FILE
        else:
            self.log_file_path = log_file
        self._ensure_data_directory()

    def _ensure_data_directory(self):
        """Ensures the data directory for the log file exists."""
        log_dir = os.path.dirname(self.log_file_path)
        if log_dir and not os.path.exists(log_dir):
            try:
                os.makedirs(log_dir)
                print(f"[{self.name}] Created directory: {log_dir}")
            except OSError as e:
                print(f"[{self.name}] Error creating directory {log_dir}: {e}")
                # Decide if this should raise an exception or just fail gracefully
                # For now, it prints and continues; logging might fail if dir not created

    def execute(self, message: str, level: str = "INFO"):
        """
        Logs a message to the configured log file.

        Args:
            message (str): The message to log.
            level (str, optional): The log level (e.g., INFO, WARNING, ERROR, DEBUG). Defaults to "INFO".

        Returns:
            bool: True if logging was successful, False otherwise.
        """
        try:
            # Ensure directory exists, in case it wasn't created at init or got deleted
            self._ensure_data_directory()

            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_entry = f"[{timestamp}] [{level.upper()}] - {message}\n"

            with open(self.log_file_path, "a") as f:
                f.write(log_entry)
            # print(f"[{self.name}] Logged: {message}") # Optional: for console feedback
            return True
        except Exception as e:
            print(f"[{self.name}] Error logging message '{message}': {e}")
            return False

if __name__ == '__main__':
    # Example Usage (for direct testing of the skill file)
    skill = LogSkill()
    skill.execute("This is an info message.")
    skill.execute("This is a warning.", level="WARNING")
    skill.execute("This is a critical error!", level="ERROR")

    # Test with a different log file path
    custom_log_path = "AgentWorkbench/data/custom_test_log.log"
    custom_skill = LogSkill(log_file=custom_log_path)
    custom_skill.execute("This is a custom log info message.")
    custom_skill.execute("This is a custom log warning.", level="WARNING")

    print(f"Check '{skill.log_file_path}' and '{custom_log_path}' for output.")
