from pydantic import BaseModel, Field
from typing import Optional

class ColumnResponse(BaseModel):
    id: int
    name: str
    order: int

class ColumnUpdate(BaseModel):
    name: Optional[str] = Field()
    order: Optional[int] = Field()

class ColumnReorder(BaseModel):
    id: int
    order: int

class ColumnCreate(BaseModel):
    name: str
    order: Optional[int] = 0
    board_id: int