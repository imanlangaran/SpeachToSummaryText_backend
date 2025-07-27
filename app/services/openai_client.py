import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

_openai_client: OpenAI | None = None

def get_openai_client() -> OpenAI:
    global _openai_client
    if _openai_client is None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise EnvironmentError("OPENAI_API_KEY not found in environment variables.")
        _openai_client = OpenAI(api_key=api_key)
    return _openai_client
