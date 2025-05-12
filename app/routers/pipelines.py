from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
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


class StepDefinition(BaseModel):
    name: str
    params: dict[str, str] = {}
    task_id: str | None = None


class PipelineCreateRequest(BaseModel):
    steps: list[StepDefinition]
    input_data: str


class StepStatus(BaseModel):
    task_id: str
    state: str


class PipelineStatusResponse(BaseModel):
    pipeline_id: str
    input_data: str
    steps: list[StepStatus]
    result: str | None = None


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
