from fastapi import APIRouter, HTTPException
from worker.tasks import summarize, translate, rewrite
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


class RewriteRequest(BaseTaskRequest):
    pass


@router.post('/summarize')
def summarize_text(request: SummarizeRequest):
    task = summarize.delay(request.text, request.model)
    return {'task_id': task.id}


@router.post('/translate')
def translate_text(request: TranslateRequest):
    task = translate.delay(request.text, request.target_language, request.model)
    return {'task_id': task.id}


@router.post('/rewrite')
def rewrite_text(request: RewriteRequest):
    task = rewrite.delay(request.text, request.model)
    return {'task_id': task.id}
