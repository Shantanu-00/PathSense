from openai import OpenAI
from typing import Dict
import json
from app.config.settings import DEEPSEEK_API_KEY


class DeepSeekClient:
    def __init__(self):
        self.client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url="https://api.deepseek.com")

    def extract_intent(self, query: str) -> Dict:
        prompt = f"""
        Extract the following from this query in valid JSON format only:
        -"business_type"(e.g., "pharmacy" or "restaurant,cafe,fast_food" for places to eat)
        -"location"(City/area, full if provided e.g. "Otur, Pune, Maharashtra")
        -"action"(e.g., "plan route","find shops")

        Query: "{query}"

        Return ONLY JSON, no other text.
        Example: {{"business_type": "pharmacy", "location": "Pune", "action": "find shops"}}
        """

        response = self.client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=200
        )

        llm_response = response.choices[0].message.content

        # Extract JSON substring
        json_start = llm_response.find("{")
        json_end = llm_response.rfind("}") + 1
        if json_start == -1 or json_end == -1:
            return {"business_type": None, "location": None, "action": None}

        json_str = llm_response[json_start:json_end]
        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            return {"business_type": None, "location": None, "action": None}

    def get_response(self, prompt: str) -> str:
        response = self.client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=500
        )
        return response.choices[0].message.content