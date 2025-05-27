import os
import sys
import unittest
from unittest.mock import patch

# Add the object-detection directory to the system path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'object-detection')))

from config import OpenAIConfig

class TestOpenAIConfig(unittest.TestCase):
    @patch.dict(os.environ, {"AZURE_OPENAI_API_KEY": "test_key"})
    def test_configure_openai_with_valid_key(self):
        try:
            OpenAIConfig.configure_openai()
            self.assertEqual(OpenAIConfig.api_key, "test_key")
        except Exception as e:
            self.fail(f"configure_openai() raised an exception unexpectedly: {e}")

    @patch.dict(os.environ, {}, clear=True)
    def test_configure_openai_without_key(self):
        OpenAIConfig.api_key = None  # Ensure the api_key is reset
        with self.assertRaises(ValueError) as context:
            OpenAIConfig.configure_openai()
        self.assertTrue("API key is not set" in str(context.exception))

if __name__ == "__main__":
    unittest.main()
