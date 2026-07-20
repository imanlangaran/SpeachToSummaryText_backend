import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

_openai_client: OpenAI | None = None


def get_openai_client() -> OpenAI:
    """Return an OpenAI client, routing to Groq if configured.

    Priority:
      1. If AI_PROVIDER=groq or GROQ_API_KEY is set → use Groq endpoint.
      2. Otherwise → use the standard OpenAI API.
    """
    global _openai_client
    if _openai_client is not None:
        return _openai_client

    groq_api_key = os.getenv("GROQ_API_KEY")
    provider = os.getenv("AI_PROVIDER", "").strip().lower()
    use_groq = provider == "groq" or (groq_api_key and provider != "openai")

            
    if use_groq:
        if not groq_api_key:
            raise EnvironmentError(
                "GROQ_API_KEY is required when AI_PROVIDER=groq. "
                "Get a free key at https://console.groq.com/keys"
            )
        _openai_client = OpenAI(
            api_key=groq_api_key,
            base_url="https://api.groq.com/openai/v1",
        )
    else:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise EnvironmentError(
                "OPENAI_API_KEY not found in environment variables. "
                "Set OPENAI_API_KEY or configure GROQ_API_KEY for free transcription."
            )
        _openai_client = OpenAI(api_key=api_key)

    return _openai_client
