from worker.celery import app
from openai import OpenAI

client = OpenAI()


@app.task
def summarize(text: str, model: str = None):
    SYSTEM_PROMPT = (
        "You are a summarization assistant. Your task is to generate clear, concise, and well-structured summaries. "
        "Focus on reducing the original text length while preserving all key information, main points, and critical details. "
        "Remove redundancies, examples, and non-essential elaborations. Maintain a logical flow and ensure clarity throughout the summary."
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
