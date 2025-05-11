from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Dict, Optional
from worker.tasks import summarize, translate, rewrite
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

    for step in request.steps:
        step.task_id = str(uuid.uuid4())

    s = None

    for i, step in enumerate(request.steps[::-1]):
        celery_task = get_task_by_name(step.name)

        if i == len(request.steps)-1:
            s = celery_task.signature(kwargs={'text': request.input_data, **step.params}, task_id=step.task_id, link=s)
        elif s == None:
            s = celery_task.signature(kwargs={**step.params}, task_id=step.task_id)
        else:
            s = celery_task.signature(kwargs={**step.params}, task_id=step.task_id, link=s)

    result = s.delay()

    # redis_instance.hset(f'pipeline:{pipeline_id}', mapping={
    #     'input_data': request.input_data,
    #     'steps': json.dumps([step.dict() for step in request.steps])
    # })

    return {'pipeline_id': pipeline_id}


@router.get('/{pipeline_id}')
def get_pipeline_result(pipeline_id: str):
    result = redis_instance.hgetall(f'pipeline:{pipeline_id}')

    result = {k.decode(): v.decode() for k, v in result.items()}

    result['steps'] = json.loads(result['steps'])
    return result


def get_task_by_name(name: str):
    mapping = {
        'summarize': summarize,
        'translate': translate,
        'rewrite': rewrite,
    }

    return mapping[name]
