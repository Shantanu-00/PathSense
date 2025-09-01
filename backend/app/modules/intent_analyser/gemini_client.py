import json
import google.generativeai as genai
from typing import Dict
from app.config.settings import GEMINI_API_KEY

class GeminiClient:
    def __init__(self):
        genai.configure(api_key=GEMINI_API_KEY)
        self.model = genai.GenerativeModel("gemini-1.5-flash")

    def extract_intent(self, query: str) -> Dict:
        prompt = f"""
        Extract the following from this query in valid JSON format only:
        - "business_type" (e.g., "pharmacy" or "restaurant,cafe,fast_food" for places to eat)
        - "location" (City/area, full if provided e.g. "Otur, Pune, Maharashtra")
        - "action" (e.g., "plan route","find shops")

        Query: "{query}"

        Return ONLY JSON, no other text.
        Example: {{"business_type": "pharmacy", "location": "Pune", "action": "find shops"}}
        """

        try:
            response = self.model.generate_content(prompt)
            text_response = response.text.strip()

            json_start = text_response.find('{')
            json_end = text_response.rfind('}') + 1
            json_str = text_response[json_start:json_end]

            return json.loads(json_str)
        except Exception as e:
            print("Gemini failed:", e)
            return {"business_type": None, "location": None, "action": None}

    def get_response(self, prompt: str) -> str:
        response = self.model.generate_content(prompt)
        return response.text.strip()