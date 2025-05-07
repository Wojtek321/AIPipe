from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Dict
import uuid

router = APIRouter(
    prefix='/pipelines'
)


class Step(BaseModel):
    name: str
    params: Dict[str, str] = {}


class CreatePipelineRequest(BaseModel):
    steps: List[Step]
    input_data: str


@router.post('/')
def create_pipeline(request: CreatePipelineRequest):
    pipeline_id = str(uuid.uuid4())

    return {'pipeline_id': pipeline_id}
