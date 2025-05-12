from fastapi import APIRouter
from redis import Redis
import uuid
import json

from .utils import get_task_by_name, get_pipeline_status
from .schemas import PipelineCreateRequest, PipelineStatusResponse

router = APIRouter(
    prefix='/pipelines'
)

redis_instance = Redis.from_url('redis://redis:6379/1')


@router.post('/', response_model=PipelineStatusResponse)
def create_pipeline(request: PipelineCreateRequest):
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

    input_data, steps, result = get_pipeline_status(pipeline_id)

    return PipelineStatusResponse(
        pipeline_id=pipeline_id,
        input_data=input_data,
        steps=steps,
        result=result
    )


@router.get('/{pipeline_id}', response_model=PipelineStatusResponse)
def get_pipeline_result(pipeline_id: str):
    input_data, steps, result = get_pipeline_status(pipeline_id)

    return PipelineStatusResponse(
        pipeline_id=pipeline_id,
        input_data=input_data,
        steps=steps,
        result=result
    )
