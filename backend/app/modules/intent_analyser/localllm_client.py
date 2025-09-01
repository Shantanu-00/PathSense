import json
from typing import Dict
from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM


class LocalLLMClient:
    def __init__(
        self,
        intent_model: str = "google/flan-t5-base",
        chat_model: str = "tiiuae/falcon-1b-instruct"
    ):
        self.intent_model_name = intent_model
        self.chat_model_name = chat_model
        self.intent_llm = None
        self.chat_llm = None
        self.intent_tokenizer = None
        self.chat_tokenizer = None

    def _initialize_intent_llm(self):
        if self.intent_llm is None:
            print(f"Loading intent model: {self.intent_model_name}")
            self.intent_llm = pipeline(
                "text2text-generation",
                model=self.intent_model_name,
                device_map="auto"
            )
            self.intent_tokenizer = AutoTokenizer.from_pretrained(self.intent_model_name)

    def _initialize_chat_llm(self):
        if self.chat_llm is None:
            print(f"Loading chat model: {self.chat_model_name}")
            self.chat_llm = pipeline(
                "text-generation",
                model=self.chat_model_name,
                tokenizer=self.chat_model_name,
                device_map="auto"
            )
            self.chat_tokenizer = AutoTokenizer.from_pretrained(self.chat_model_name)

    def extract_intent(self, query: str) -> Dict:
        self._initialize_intent_llm()

        prompt = f"""
        Extract intent from the following query and return ONLY valid JSON:
        {{
            "business_type": "... (e.g. restaurant,cafe for places to eat)",
            "location": "... (full location)",
            "action": "..."
        }}
        Query: "{query}"
        """

        try:
            response = self.intent_llm(
                prompt,
                max_new_tokens=128,
                temperature=0.1,
                pad_token_id=self.intent_tokenizer.eos_token_id
            )
            generated_text = response[0]["generated_text"]

            print("RAW INTENT OUTPUT:", generated_text)  # Debug

            json_start = generated_text.find('{')
            json_end = generated_text.rfind('}') + 1

            if json_start != -1 and json_end != -1:
                json_str = generated_text[json_start:json_end]
                return json.loads(json_str)

        except Exception as e:
            print("Error parsing intent:", e)

        return {"business_type": None, "location": None, "action": None}

    def get_response(self, prompt: str) -> str:
        self._initialize_chat_llm()
        response = self.chat_llm(
            prompt,
            max_new_tokens=256,
            temperature=0.7,
            do_sample=True,
            pad_token_id=self.chat_tokenizer.eos_token_id
        )
        return response[0]["generated_text"].strip()
