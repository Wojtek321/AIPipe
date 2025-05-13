from worker.celery import app
from openai import OpenAI

client = OpenAI()


@app.task
def expand(text: str, model: str = None):
    SYSTEM_PROMPT = (
        "You are a text expansion assistant. Your task is to enrich and elaborate the given input text by adding relevant details, explanations, or context. "
        "Maintain the original meaning and intent, but improve the clarity, informativeness, and depth. "
        "Use a coherent and natural writing style without introducing unrelated information. Avoid repetition. "
        "Ensure that the expanded text remains in the same language as the original input."
    )

    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Expand the text:\n\n{text}"}
        ],
    )

    response = completion.choices[0].message.content
    return response
