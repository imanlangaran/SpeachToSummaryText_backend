from app.services.openai_client import get_openai_client


def summarise_text(text, prompt) -> str:
    try:
        client = get_openai_client()
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


def summarise_text_assistant(text: str, assistant_id: str | None, prompt_obj) -> str:
    if not assistant_id:
        return summarise_text(text, prompt_obj)
    try:
        client = get_openai_client()
        # Create a thread and run the assistant
        thread = client.beta.threads.create(
            messages=[{"role": "user", "content": text}]
        )

        run = client.beta.threads.runs.create_and_poll(
            thread_id=thread.id,
            assistant_id=assistant_id,
        )

        if run.status != "completed":
            raise RuntimeError(f"assistant run failed with status: {run.status}")

        # Fetch messages from the thread
        messages = client.beta.threads.messages.list(thread_id=thread.id)

        # Extract the latest assistant message
        for msg in messages.data:
            if msg.role == "assistant":
                return msg.content[0].text.value.strip()

        raise RuntimeError("no response from assistant")

    except Exception as error:
        raise RuntimeError(f"gpt summarization failed: {error}")
