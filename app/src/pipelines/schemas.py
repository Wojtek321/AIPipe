from pydantic import BaseModel


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
