import unittest
from unittest.mock import patch, MagicMock
# Assuming 'translators' library might raise specific errors.
# We'll import 'translators' itself to reference its potential errors.
import translators as ts
from skills import TranslationSkill # Assuming correct import

class TestTranslationSkill(unittest.TestCase):

    def setUp(self):
        self.skill = TranslationSkill()

    # Patch the 'translate_text' function within the 'translation_skill' module's scope
    @patch('skills.translation_skill.ts.translate_text')
    @patch('builtins.print')
    def test_execute_success_auto_source(self, mock_print, mock_translate_text):
        mock_translate_text.return_value = "Hola Mundo"

        text_to_translate = "Hello World"
        target_language = "es"
        expected_print_snippet = f"Translated '{text_to_translate}' (auto -> {target_language}): 'Hola Mundo'"

        result = self.skill.execute(text_to_translate, target_language)

        self.assertEqual(result, "Hola Mundo")
        mock_translate_text.assert_called_once_with(
            query_text=text_to_translate,
            to_language=target_language
            # from_language is not passed when source is 'auto' in skill logic
        )
        # Check if the expected snippet is part of any print call
        self.assertTrue(any(expected_print_snippet in call_args[0][0] for call_args in mock_print.call_args_list))


    @patch('skills.translation_skill.ts.translate_text')
    @patch('builtins.print')
    def test_execute_success_with_source_language(self, mock_print, mock_translate_text):
        mock_translate_text.return_value = "Hello World"

        text_to_translate = "Hola Mundo"
        target_language = "en"
        source_language = "es"
        expected_print_snippet = f"Translated '{text_to_translate}' ({source_language} -> {target_language}): 'Hello World'"

        result = self.skill.execute(text_to_translate, target_language, source_language)

        self.assertEqual(result, "Hello World")
        mock_translate_text.assert_called_once_with(
            query_text=text_to_translate,
            from_language=source_language,
            to_language=target_language
        )
        self.assertTrue(any(expected_print_snippet in call_args[0][0] for call_args in mock_print.call_args_list))

    @patch('builtins.print')
    def test_execute_no_text_to_translate(self, mock_print):
        result = self.skill.execute("", "es")
        self.assertIsNone(result)
        mock_print.assert_any_call(f"[{self.skill.name}] Error: No text provided for translation.")

    @patch('builtins.print')
    def test_execute_no_target_language(self, mock_print):
        result = self.skill.execute("Some text", "")
        self.assertIsNone(result)
        mock_print.assert_any_call(f"[{self.skill.name}] Error: No target language specified.")

    @patch('skills.translation_skill.ts.translate_text', side_effect=ts.TranslatorError("Service unavailable"))
    @patch('builtins.print')
    def test_execute_translator_library_error(self, mock_print, mock_translate_text_error):
        text_to_translate = "Hello"
        target_language = "fr"

        result = self.skill.execute(text_to_translate, target_language)

        self.assertIsNone(result)
        mock_translate_text_error.assert_called_once()
        mock_print.assert_any_call(f"[{self.skill.name}] Translation Error (from 'translators' library): Service unavailable")

    @patch('skills.translation_skill.ts.translate_text', side_effect=Exception("Unexpected generic error"))
    @patch('builtins.print')
    def test_execute_unexpected_error(self, mock_print, mock_translate_text_unexpected_error):
        text_to_translate = "Bonjour"
        target_language = "en"

        result = self.skill.execute(text_to_translate, target_language)

        self.assertIsNone(result)
        mock_translate_text_unexpected_error.assert_called_once()
        mock_print.assert_any_call(f"[{self.skill.name}] An unexpected error occurred during translation: Unexpected generic error")


if __name__ == "__main__":
    unittest.main()
