from pydantic import BaseModel
from typing import Literal


class BaseTaskRequest(BaseModel):
    text: str
    model: Literal['gpt'] = 'gpt'


class SummarizeRequest(BaseTaskRequest):
    pass


class TranslateRequest(BaseTaskRequest):
    target_language: str


class RewriteRequest(BaseTaskRequest):
    pass


class ExpandRequest(BaseTaskRequest):
    pass


class TaskStatusResponse(BaseModel):
    task_id: str
    state: str
    result: str | None = None
    error: str | None = None
