import translators as ts
from core import BaseSkill

class TranslationSkill(BaseSkill):
    """A skill to translate text between languages using the 'translators' library."""

    def __init__(self, name="TranslationSkill",
                 description="Translates text to a target language."):
        super().__init__(name, description)
        # No specific API key needed at init time for the 'translators' library,
        # as it tries various free/public services.

    def execute(self, text_to_translate: str, target_language: str, source_language: str = "auto"):
        """
        Translates the given text to the target language.

        Args:
            text_to_translate (str): The text to be translated.
            target_language (str): The language code of the target language (e.g., 'fr', 'es').
            source_language (str, optional): The language code of the source language.
                                             Defaults to "auto" for auto-detection.

        Returns:
            str: The translated text, or None if an error occurs.
        """
        if not text_to_translate:
            print(f"[{self.name}] Error: No text provided for translation.")
            return None
        if not target_language:
            print(f"[{self.name}] Error: No target language specified.")
            return None

        try:
            # translators.translate_text parameters:
            # query_text, translator='bing', from_language='en', to_language='zh', **kwargs
            # We will use the default translator which tries multiple services.
            # Note: The library might be slow if it tries many services.
            # For specific language pairs, specifying the translator might be faster if known.

            # Ensure source_language is passed correctly; if 'auto', library handles it.
            if source_language.lower() == "auto":
                translated_text = ts.translate_text(
                    query_text=text_to_translate,
                    to_language=target_language
                )
            else:
                translated_text = ts.translate_text(
                    query_text=text_to_translate,
                    from_language=source_language,
                    to_language=target_language
                )

            print(f"[{self.name}] Translated '{text_to_translate}' ({source_language if source_language else 'auto'} -> {target_language}): '{translated_text}'")
            return translated_text

        except ts.TranslatorError as e: # Catching specific library error
            print(f"[{self.name}] Translation Error (from 'translators' library): {e}")
        except Exception as e:
            # Catching other potential errors (network if library uses online services, etc.)
            print(f"[{self.name}] An unexpected error occurred during translation: {e}")

        return None

if __name__ == '__main__':
    # This example might be slow or vary in success depending on the 'translators' library's backend services.
    print("Attempting to use TranslationSkill (uses 'translators' library)...")

    translation_skill = TranslationSkill()

    text1 = "Hello, world!"
    target_lang1 = "es" # Spanish
    print(f"\nTranslating '{text1}' to '{target_lang1}':")
    translated1 = translation_skill.execute(text_to_translate=text1, target_language=target_lang1)
    if translated1:
        print(f"Result: {translated1}")
    else:
        print("Translation failed or returned no text.")

    text2 = "Bonjour le monde!"
    target_lang2 = "en" # English
    source_lang2 = "fr" # French
    print(f"\nTranslating '{text2}' from '{source_lang2}' to '{target_lang2}':")
    translated2 = translation_skill.execute(text_to_translate=text2, target_language=target_lang2, source_language=source_lang2)
    if translated2:
        print(f"Result: {translated2}")
    else:
        print("Translation failed or returned no text.")

    text3 = "Wie geht es Ihnen?"
    target_lang3 = "en"
    print(f"\nTranslating '{text3}' (auto source) to '{target_lang3}':")
    translated3 = translation_skill.execute(text_to_translate=text3, target_language=target_lang3) # Auto-detect source
    if translated3:
        print(f"Result: {translated3}")
    else:
        print("Translation failed or returned no text.")

    text4 = "Invalid text for some reason"
    target_lang4 = "xx" # Invalid language code
    print(f"\nAttempting to translate to invalid language '{target_lang4}':")
    translated4 = translation_skill.execute(text_to_translate=text4, target_language=target_lang4)
    if translated4:
        print(f"Result: {translated4}") # Should ideally fail
    else:
        print("Translation failed as expected (or returned no text).")
