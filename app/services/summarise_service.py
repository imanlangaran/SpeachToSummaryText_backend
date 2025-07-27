from app.services.openai_client import get_openai_client

client = get_openai_client()

def summarise_text(text, prompt) -> str:
    try:
        response = client.chat.completions.create(
            model="gpt-4.1",
            messages=[
                {
                    "role": "system",
                    "content": f"تو یک دستیار هستی که متن‌های فارسی را خلاصه می‌کنی. {prompt}",
                },
                {"role": "user", "content": text},
            ],
        )

        summary = response.choices[0].message.content
        return summary.strip()

    except Exception as error:
        raise RuntimeError(f"gpt summarization failed: {error}")
