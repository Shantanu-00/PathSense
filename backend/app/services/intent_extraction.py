 # app/services/intent_extraction.py
from typing import Dict
from app.modules.intent_analyser.deepseek_client import DeepSeekClient
from app.modules.intent_analyser.localllm_client import LocalLLMClient
from app.modules.intent_analyser.gemini_client import GeminiClient
from app.utils.exceptions import LLMFailedError
from app.config.logging import logger

class IntentExtractionServices:
    def __init__(self):
        self.deepseek_client = DeepSeekClient()
        self.local_llm_client = LocalLLMClient()
        self.gemini_client = GeminiClient()

    def extract_intent(self, query: str) -> Dict:
        try:
            return self.deepseek_client.extract_intent(query)
        except Exception as e:
            logger.warning(f"Deepseek failed: {str(e)}")

        try:
            return self.gemini_client.extract_intent(query)
        except Exception as e:
            logger.warning(f"Gemini failed: {str(e)}")

        try:
            local_result = self.local_llm_client.extract_intent(query)
            if local_result and any(local_result.values()):
                return local_result
        except Exception as e:
            logger.warning(f"Local LLM failed: {str(e)}")

        raise LLMFailedError("All intent extraction methods failed")


intent_extraction_service = IntentExtractionServices()