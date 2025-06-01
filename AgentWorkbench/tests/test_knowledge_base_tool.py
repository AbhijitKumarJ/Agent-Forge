import unittest
from unittest.mock import patch
import io
from tools import KnowledgeBaseTool # Assuming tools are importable this way

class TestKnowledgeBaseTool(unittest.TestCase):

    def setUp(self):
        self.tool = KnowledgeBaseTool(name="TestKBTool", description="A test KB tool.")

    @patch('sys.stdout', new_callable=io.StringIO)
    def test_use_store_new_qa_pair(self, mock_stdout):
        question = "What is AgentWorkbench?"
        answer = "A modular platform for AI agents."
        expected_print = f"[KnowledgeBaseTool] Stored: '{question}' -> '{answer}'\n"

        result = self.tool.use(question, answer=answer)

        self.assertTrue(result)
        self.assertEqual(self.tool.kb.get(question), answer) # Check internal state
        self.assertEqual(mock_stdout.getvalue(), expected_print)

    @patch('sys.stdout', new_callable=io.StringIO)
    def test_use_retrieve_existing_answer(self, mock_stdout):
        question = "What is its main feature?"
        answer = "Extensibility."
        # Pre-populate the KB for this test
        self.tool.kb[question] = answer

        expected_print = f"[KnowledgeBaseTool] Retrieved: '{question}' -> '{answer}'\n"

        retrieved_answer = self.tool.use(question) # answer is None

        self.assertEqual(retrieved_answer, answer)
        self.assertEqual(mock_stdout.getvalue(), expected_print)

    @patch('sys.stdout', new_callable=io.StringIO)
    def test_use_retrieve_non_existing_answer(self, mock_stdout):
        question = "What is its color?"
        expected_print = f"[KnowledgeBaseTool] Retrieved: '{question}' -> 'None'\n"

        retrieved_answer = self.tool.use(question)

        self.assertIsNone(retrieved_answer)
        self.assertEqual(mock_stdout.getvalue(), expected_print)

    @patch('sys.stdout', new_callable=io.StringIO)
    def test_use_update_existing_answer(self, mock_stdout):
        question = "What is AgentWorkbench?"
        initial_answer = "A platform."
        updated_answer = "A super cool platform for AI agents!"

        # Store initial answer
        self.tool.use(question, answer=initial_answer)
        mock_stdout.truncate(0) # Clear stdout buffer
        mock_stdout.seek(0)   # Reset buffer position

        expected_print_update = f"[KnowledgeBaseTool] Stored: '{question}' -> '{updated_answer}'\n"

        # Update the answer
        result_update = self.tool.use(question, answer=updated_answer)

        self.assertTrue(result_update)
        self.assertEqual(self.tool.kb.get(question), updated_answer)
        self.assertEqual(mock_stdout.getvalue(), expected_print_update)

    @patch('sys.stdout', new_callable=io.StringIO)
    def test_use_store_and_retrieve_multiple_qa(self, mock_stdout):
        q1, a1 = "Q1", "A1"
        q2, a2 = "Q2", "A2"

        # Store Q1
        self.tool.use(q1, answer=a1)
        # Store Q2
        self.tool.use(q2, answer=a2)

        mock_stdout.truncate(0)
        mock_stdout.seek(0)

        # Retrieve Q1
        expected_print_q1 = f"[KnowledgeBaseTool] Retrieved: '{q1}' -> '{a1}'\n"
        self.assertEqual(self.tool.use(q1), a1)
        self.assertIn(expected_print_q1, mock_stdout.getvalue()) # Check if print is there

        mock_stdout.truncate(0) # Clear for next retrieval check
        mock_stdout.seek(0)

        # Retrieve Q2
        expected_print_q2 = f"[KnowledgeBaseTool] Retrieved: '{q2}' -> '{a2}'\n"
        self.assertEqual(self.tool.use(q2), a2)
        self.assertIn(expected_print_q2, mock_stdout.getvalue())

    def test_use_case_sensitivity_of_questions(self):
        question_lower = "key"
        answer_lower = "value_lower"
        question_upper = "KEY"
        answer_upper = "value_upper"

        self.tool.use(question_lower, answer=answer_lower)
        self.tool.use(question_upper, answer=answer_upper)

        self.assertEqual(self.tool.use(question_lower), answer_lower)
        self.assertEqual(self.tool.use(question_upper), answer_upper)
        self.assertNotEqual(self.tool.use(question_lower), answer_upper)


if __name__ == "__main__":
    unittest.main()
