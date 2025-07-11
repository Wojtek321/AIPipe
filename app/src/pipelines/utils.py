from fastapi import HTTPException
from celery.result import AsyncResult
from redis import Redis
import json

from worker.tasks import summarize, rewrite, translate, expand
from worker.celery import app
from .schemas import StepStatus
from .constants import PIPELINE_REDIS_PREFIX


def save_pipeline_to_redis(pipeline_id: str, input_data: str, task_ids: list[str], redis_instance: Redis):
    key = f'{PIPELINE_REDIS_PREFIX}{pipeline_id}'

    redis_instance.hset(key, mapping={
        'input_data': input_data,
        'tasks': json.dumps(task_ids)
    })


def get_pipeline_status(pipeline_id: str, redis_instance: Redis):
    pipeline = redis_instance.hgetall(f'{PIPELINE_REDIS_PREFIX}{pipeline_id}')

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
        'expand': expand,
    }

    return mapping[name]
