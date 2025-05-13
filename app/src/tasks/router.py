from fastapi import APIRouter
from celery.result import AsyncResult

from worker.celery import app
from worker.tasks import summarize, rewrite, translate, expand
from .schemas import SummarizeRequest, RewriteRequest, TranslateRequest, TaskStatusResponse, ExpandRequest

router = APIRouter(
    prefix='/tasks'
)


@router.get('/{task_id}', response_model=TaskStatusResponse)
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


@router.post('/summarize', response_model=TaskStatusResponse)
def summarize_text(request: SummarizeRequest):
    return launch_task(summarize, request.text, request.model)


@router.post('/translate', response_model=TaskStatusResponse)
def translate_text(request: TranslateRequest):
    return launch_task(translate, request.text, request.target_language, request.model)


@router.post('/rewrite', response_model=TaskStatusResponse)
def rewrite_text(request: RewriteRequest):
    return launch_task(rewrite, request.text, request.model)


@router.post('/expand', response_model=TaskStatusResponse)
def expand_text(request: ExpandRequest):
    return launch_task(expand, request.text, request.model)


def launch_task(task, *args, **kwargs):
    task = task.delay(*args, **kwargs)
    return {
        'task_id': task.id,
        'state': task.state
    }
