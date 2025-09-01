from typing import Dict, List, Tuple
import json, re
from app.modules.intent_analyser.deepseek_client import DeepSeekClient
from app.modules.intent_analyser.gemini_client import GeminiClient
from app.modules.intent_analyser.localllm_client import LocalLLMClient
from app.services.places_service import PlacesServices
from app.schemas.places import Place
from app.utils.session import get_session, store_in_session
from app.utils.exceptions import LLMFailedError
from app.schemas.chat import ChatResponse
from app.config.logging import logger


class ChatService:
    def __init__(self):
        self.deepseek_client = DeepSeekClient()
        self.gemini_client = GeminiClient()
        self.local_llm_client = LocalLLMClient()

    async def handle_chat(self, query: str, session_id: str | None) -> ChatResponse:
        session_id, state = get_session(session_id)
        state["session_id"] = session_id
        logger.info(f"[Session: {session_id}] Received chat query: {query}")

        if "history" not in state:
            state["history"] = []
        if "intent" not in state:
            state["intent"] = {}

        state["history"].append({"role": "user", "content": query})

        # Process query
        response, updated_intent, new_places = await self._process(
            state["history"], state["intent"], state
        )

        # Update state
        state["intent"] = updated_intent
        if new_places:
            # Store places in session route - avoid duplicates
            route = state.setdefault('route', {"places": [], "start": None, "end": None, "last_query": {}})
            
            # Get existing coordinates to avoid duplicates
            existing_coords = {(p.latitude, p.longitude) for p in route['places']}
            if route.get('start'):
                existing_coords.add((route['start'].latitude, route['start'].longitude))
            if route.get('end'):
                existing_coords.add((route['end'].latitude, route['end'].longitude))
            
            # Filter out duplicates
            unique_new_places = [p for p in new_places if (p.latitude, p.longitude) not in existing_coords]
            
            # Add only unique places
            route['places'].extend(unique_new_places)
            
        state["history"].append({"role": "assistant", "content": response})
        store_in_session(session_id, state)
    
        logger.info(f"[Session: {session_id}] Response prepared: {response}")

        # CHANGED: Return full current route state
        route = state.get('route', {})
        return ChatResponse(
            message=response,
            places=route.get('places', []),
            start=route.get('start'),
            end=route.get('end'),
            session_id=session_id
        )

    async def _process(self, history: List[Dict], current_intent: Dict, state: Dict) -> Tuple[str, Dict, List[Place] | None]:
        prompt = self._build_prompt(history, current_intent)
        try:
            llm_response = self.deepseek_client.get_response(prompt)
        except Exception as e:
            logger.warning(f"DeepSeek failed: {e}")
            try:
                llm_response = self.gemini_client.get_response(prompt)
            except Exception as e:
                logger.warning(f"Gemini failed: {e}")
                try:
                    llm_response = self.local_llm_client.get_response(prompt)
                except Exception as e:
                    logger.warning(f"Local LLM failed: {e}")
                    raise LLMFailedError("All LLMs failed")

        logger.info(f"[Session: {state.get('session_id')}] LLM response: {llm_response}")
        message, new_intent, places = await self._parse_response(llm_response, current_intent, state)
        return message, new_intent, places

    def _build_prompt(self, history: List[Dict], current_intent: Dict) -> str:
        history_str = "\n".join([f"{m['role'].capitalize()}: {m['content']}" for m in history])
        return f"""
You are a friendly route planning chatbot.
Goal: Extract intent for finding places and optimizing routes.
Fields:
- business_type: str or comma-separated (e.g. "restaurant,cafe,fast_food" for 'places to eat')
- location: str, full (e.g. "Otur, Pune, Maharashtra"), handle specifics/ambiguities by asking (e.g. "Akola in Maharashtra or elsewhere?")
- count: int 1-10, default 5, ask if missing
- action: "find_places" or "plan_route"

Handle grammar, singular/plural, variations (e.g. "hotels" -> "hotel").
Greet casually if greeted.
Steer unrelated queries back.
If incomplete, ask one question at a time.
If complete, respond confirming (e.g. "Great, finding {{count}} {{business_type}} in {{location}}"), then ###INTENT### followed by JSON (raw JSON, do NOT wrap in ```).

Current partial intent: {json.dumps(current_intent)}

Conversation:
{history_str}

Respond:
"""

    async def _parse_response(self, response: str, current_intent: Dict, state: Dict) -> Tuple[str, Dict, List[Place] | None]:
        if "###INTENT###" in response:
            parts = response.split("###INTENT###")
            message = parts[0].strip()
            json_str = parts[1].strip()

            # cleanup for ```json
            if json_str.startswith("```"):
                json_str = json_str.strip("`")
                if json_str.lower().startswith("json"):
                    json_str = json_str[4:].strip()

            try:
                new_intent = json.loads(json_str)

                # normalize business_type
                if "business_type" in new_intent:
                    new_intent["business_type"] = self._normalize_business_type(new_intent["business_type"])

                # fill missing parameters from session
                if "business_type" not in new_intent:
                    new_intent["business_type"] = state["intent"].get("business_type", "restaurant")
                if "location" not in new_intent:
                    new_intent["location"] = state["intent"].get("location", "Pune")
                if "count" not in new_intent:
                    new_intent["count"] = state["intent"].get("count", 5)

                logger.info(f"[Session: {state.get('session_id')}] Parsed intent: {new_intent}")

                if all(key in new_intent for key in ["business_type", "location", "count", "action"]):
                    places = None
                    if new_intent["action"] in ["find_places", "plan_route"]:
                        logger.info(f"[Session: {state.get('session_id')}] Calling get_places with: "
                                    f"business_type={new_intent['business_type']}, "
                                    f"location={new_intent['location']}, count={new_intent['count']}")
                        result = await PlacesServices.get_places(
                            new_intent["business_type"],
                            new_intent["location"],
                            new_intent["count"],
                            session_id=state.get("session_id")
                        )
                        places = result.places if result else None
                    return message, new_intent, places

            except json.JSONDecodeError as e:
                logger.warning(f"Invalid intent JSON: {e}")

        return response.strip(), current_intent, None

    def _normalize_business_type(self, bt: str) -> str:
        """
        Normalize business_type to match OSM amenity_map
        """
        bt = bt.lower().strip()

        # Remove trailing "'s" (ATM's -> atm)
        bt = re.sub(r"'s$", "", bt)

        # Handle plurals
        if bt.endswith("ies"):   # universities -> university
            bt = bt[:-3] + "y"
        elif bt.endswith("es") and not bt.endswith("ses"):  # cafes -> cafe
            bt = bt[:-2]
        elif bt.endswith("s") and not bt.endswith("ss"):    # hotels -> hotel
            bt = bt[:-1]

        return bt


chat_service = ChatService()