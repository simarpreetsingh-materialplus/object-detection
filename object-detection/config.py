import openai
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set up Azure OpenAI credentials
class OpenAIConfig:
    api_type = "azure"
    api_base = "Write your Azure OpenAI endpoint here"
    api_version = "2023-06-01-preview"
    api_key = "Write your Azure OpenAI key here"
 
    @classmethod
    def configure_openai(cls):
        try:
            openai.api_type = cls.api_type
            openai.api_base = cls.api_base
            openai.api_version = cls.api_version
            openai.api_key = cls.api_key
            logger.info("OpenAI configuration set successfully.")
        except Exception as e:
            logger.error("Failed to configure OpenAI: %s", e)
            raise

# Call this at the start of your app to configure OpenAI
OpenAIConfig.configure_openai()