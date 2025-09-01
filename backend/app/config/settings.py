import os
from dotenv import load_dotenv


env_path = os.path.join(os.path.dirname(__file__),  '..', '..', '.env')
load_dotenv(dotenv_path=env_path)


DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")


if not DEEPSEEK_API_KEY:
    raise ValueError("DEEPSEEK_API_KEY not found in environment variables")