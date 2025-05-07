from fastapi import APIRouter, HTTPException
from worker.tasks import summarize

router = APIRouter(
    prefix='/tasks'
)


@router.get('/summarize')
def summarize_text(text: str, model: str = "gpt"):
    if model not in ['gpt', 'claude', 'local']:
        return HTTPException(status_code=400, detail='Invalid model type')

    task = summarize.delay(text, model)
    return {'task_id': task.id}
