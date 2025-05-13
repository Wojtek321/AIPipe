from fastapi import APIRouter, Depends
from redis import Redis
import uuid

from .utils import save_pipeline_to_redis, get_pipeline_status, get_task_by_name
from .schemas import PipelineCreateRequest, PipelineStatusResponse
from .dependencies import get_redis

router = APIRouter(
    prefix='/pipelines'
)


@router.post('/', response_model=PipelineStatusResponse)
def create_pipeline(request: PipelineCreateRequest, redis_instance: Redis = Depends(get_redis)):
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

    task_ids = [step.task_id for step in request.steps]
    save_pipeline_to_redis(pipeline_id, request.input_data, task_ids, redis_instance)

    input_data, steps, result = get_pipeline_status(pipeline_id, redis_instance)

    return {
        'pipeline_id': pipeline_id,
        'input_data': input_data,
        'steps': steps,
        'result': result,
    }


@router.get('/{pipeline_id}', response_model=PipelineStatusResponse)
def get_pipeline_result(pipeline_id: str, redis_instance: Redis = Depends(get_redis)):
    input_data, steps, result = get_pipeline_status(pipeline_id, redis_instance)

    return {
        'pipeline_id': pipeline_id,
        'input_data': input_data,
        'steps': steps,
        'result': result,
    }
