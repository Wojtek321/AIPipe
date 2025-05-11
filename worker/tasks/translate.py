from worker.celery import app
from openai import OpenAI

client = OpenAI()


@app.task
def translate(text: str, target_language: str, model: str = None, pipeline_id: str = None):
    SYSTEM_PROMPT = (
        f"You are a professional translation assistant. Translate the given text accurately and fluently into {target_language}. "
        "Preserve the original meaning, tone, and style of the text. Do not add or omit any information. "
        "Make sure the translation sounds natural to a native speaker of the target language."
    )

    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Translate the following text into {target_language}:\n\n{text}"}
        ],
    )

    response = completion.choices[0].message.content
    return response
