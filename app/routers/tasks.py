from fastapi import APIRouter, HTTPException
from worker.tasks import summarize, translate, rewrite
from worker.celery import app
from celery.result import AsyncResult
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


@router.get('/{task_id}')
def get_task_result(task_id: str):
    result = AsyncResult(task_id, app=app)

    response = {
        'task_id':  task_id,
        'state': result.state,
    }

    if result.state == 'SUCCESS':
        response['result'] = result.result
    if result.state == 'FAILURE':
        response['error'] = str(result.result)

    return response


@router.post('/summarize')
def summarize_text(request: SummarizeRequest):
    task = summarize.delay(request.text, request.model)
    return {'task_id': task.id, 'state': task.state}


@router.post('/translate')
def translate_text(request: TranslateRequest):
    task = translate.delay(request.text, request.target_language, request.model)
    return {'task_id': task.id, 'state': task.state}


@router.post('/rewrite')
def rewrite_text(request: RewriteRequest):
    task = rewrite.delay(request.text, request.model)
    return {'task_id': task.id, 'state': task.state}
