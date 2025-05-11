from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional
from worker.tasks import summarize, translate, rewrite
from worker.celery import app
from celery.result import AsyncResult
from redis import Redis
import uuid
import json

router = APIRouter(
    prefix='/pipelines'
)

redis_instance = Redis.from_url('redis://redis:6379/1')


class Step(BaseModel):
    name: str
    params: Dict[str, str] = {}
    task_id: Optional[str] = None


class CreatePipelineRequest(BaseModel):
    steps: List[Step]
    input_data: str


@router.post('/')
def create_pipeline(request: CreatePipelineRequest):
    pipeline_id = str(uuid.uuid4())

    s = None

    for i, step in enumerate(request.steps[::-1]):
        step.task_id = str(uuid.uuid4())
        celery_task = get_task_by_name(step.name)

        if i == len(request.steps)-1:
            s = celery_task.signature(kwargs={'text': request.input_data, **step.params}, task_id=step.task_id, link=s)
        elif s is None:
            s = celery_task.signature(kwargs={**step.params}, task_id=step.task_id)
        else:
            s = celery_task.signature(kwargs={**step.params}, task_id=step.task_id, link=s)

    s.delay()

    redis_instance.hset(f'pipeline:{pipeline_id}', mapping={
        'input_data': request.input_data,
        'tasks': json.dumps([step.task_id for step in request.steps])
    })

    return {'pipeline_id': pipeline_id}


@router.get('/{pipeline_id}')
def get_pipeline_result(pipeline_id: str):
    pipeline = redis_instance.hgetall(f'pipeline:{pipeline_id}')

    if not pipeline:
        raise HTTPException(status_code=404, detail='Pipeline not found')

    pipeline = {k.decode(): v.decode() for k, v in pipeline.items()}
    pipeline['tasks'] = json.loads(pipeline['tasks'])

    steps = []
    final_result = None

    for i, task_id in enumerate(pipeline['tasks']):
        result = AsyncResult(task_id, app=app)

        step = {
            'task_id': task_id,
            'state': result.state,
        }

        steps.append(step)

        if i == len(pipeline['tasks']) - 1 and result.successful():
            final_result = result.result

    return {
        'input_data': pipeline['input_data'],
        'steps': steps,
        'result': final_result,
    }


def get_task_by_name(name: str):
    mapping = {
        'summarize': summarize,
        'translate': translate,
        'rewrite': rewrite,
    }

    return mapping[name]
