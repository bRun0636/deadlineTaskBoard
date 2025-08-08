from pydantic import BaseModel, Field
from typing import Optional

class ColumnResponse(BaseModel):
    id: int
    title: str  # Изменено с name на title
    order_index: int  # Изменено с order на order_index

    model_config = {
        "from_attributes": True
    }

class ColumnUpdate(BaseModel):
    title: Optional[str] = Field()  # Изменено с name на title
    order_index: Optional[int] = Field()  # Изменено с order на order_index

    model_config = {
        "from_attributes": True
    }

class ColumnReorder(BaseModel):
    id: int
    order_index: int  # Изменено с order на order_index

    model_config = {
        "from_attributes": True
    }

class ColumnCreate(BaseModel):
    title: str  # Изменено с name на title
    order_index: Optional[int] = 0  # Изменено с order на order_index
    board_id: int

    model_config = {
        "from_attributes": True
    }