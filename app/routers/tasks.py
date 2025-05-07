from fastapi import APIRouter, HTTPException
from worker.tasks import summarize, translate
from pydantic import BaseModel
from typing import Literal

router = APIRouter(
    prefix='/tasks'
)


class BaseTaskRequest(BaseModel):
    text: str
    model: Literal['gpt'] = 'gpt'


class SummarizeRequest(BaseTaskRequest):
    pass


class TranslateRequest(BaseTaskRequest):
    target_language: str


@router.post('/summarize')
def summarize_text(request: SummarizeRequest):
    task = summarize.delay(request.text, request.model)
    return {'task_id': task.id}


@router.post('/translate')
def translate_text(request: TranslateRequest):
    task = translate.delay(request.text, request.target_language, request.model)
    return {'task_id': task.id}
