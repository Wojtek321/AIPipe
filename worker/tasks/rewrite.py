from worker.celery import app
from openai import OpenAI

client = OpenAI()


@app.task
def rewrite(text: str, model: str = None, pipeline_id: str = None):
    SYSTEM_PROMPT = (
        "You are a rewriting assistant. Your task is to rewrite the provided text to improve its clarity, flow, and style, "
        "while preserving the original meaning. Avoid changing the factual content. "
        "Make the text sound natural, fluent, and well-structured. Do not summarize or shorten it."
    )

    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Rewrite the following text:\n\n{text}"}
        ],
    )

    response = completion.choices[0].message.content
    return response
