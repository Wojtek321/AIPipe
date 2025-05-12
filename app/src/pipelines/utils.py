from fastapi import HTTPException
from celery.result import AsyncResult
from redis import Redis
import json

from worker.tasks import summarize, rewrite, translate
from worker.celery import app
from .schemas import StepStatus

redis_instance = Redis.from_url('redis://redis:6379/1')


def get_pipeline_status(pipeline_id: str):
    pipeline = redis_instance.hgetall(f'pipeline:{pipeline_id}')

    if not pipeline:
        raise HTTPException(status_code=404, detail='Pipeline not found')

    pipeline = {k.decode(): v.decode() for k, v in pipeline.items()}
    tasks_ids = json.loads(pipeline['tasks'])

    steps = []
    final_result = None

    for i, task_id in enumerate(tasks_ids):
        result = AsyncResult(task_id, app=app)
        steps.append(StepStatus(task_id=task_id, state=result.state))

        if i == len(tasks_ids) - 1 and result.successful():
            final_result = result.result

    return pipeline['input_data'], steps, final_result


def get_task_by_name(name: str):
    mapping = {
        'summarize': summarize,
        'translate': translate,
        'rewrite': rewrite,
    }

    return mapping[name]
