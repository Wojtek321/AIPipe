from worker.celery import app
from openai import OpenAI

client = OpenAI()


@app.task
def summarize(text: str, model: str):
    SYSTEM_PROMPT = (
        "You are a summarization assistant. Your task is to generate clear, concise, and well-structured summaries. "
        "Preserve all key information, main points, and important details, while removing redundant or non-essential content. "
        "Maintain logical flow and clarity throughout the summary."
    )

    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Summarize the text:\n\n{text}"}
        ],
    )

    response = completion.choices[0].message.content
    return response
