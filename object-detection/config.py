import openai
import os

# Set up Azure OpenAI credentials
class OpenAIConfig:
    api_type = "azure"
    api_base = "https://object-detection-testing.openai.azure.com/"
    api_version = "2023-06-01-preview"
    api_key = None

    @classmethod
    def configure_openai(cls):
        cls.api_key = os.getenv("AZURE_OPENAI_API_KEY")
        if not cls.api_key:
            raise ValueError("API key is not set. Please set the AZURE_OPENAI_API_KEY environment variable.")
        openai.api_type = cls.api_type
        openai.api_base = cls.api_base
        openai.api_version = cls.api_version
        openai.api_key = cls.api_key
