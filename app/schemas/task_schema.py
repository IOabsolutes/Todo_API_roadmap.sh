from pydantic import BaseModel
from enum import Enum
from typing import Optional


class IOrderByTaskEnum(str, Enum):
    id = "id"
    title = "title"
    create_at = "create_at"


class ITaskBase(BaseModel):
    title: str
    description: Optional[str]


class ITaskCreate(ITaskBase):
    pass


class ITaskUpdate(ITaskBase):
    pass


class ITaskRead(ITaskBase):
    id: int
    user_id: int
