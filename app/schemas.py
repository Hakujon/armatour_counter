from pydantic import BaseModel, Field


class BaseWorkpiece(BaseModel):
    length: int = Field(..., description="Длина заготовки")


class GroupWorkpieces(BaseWorkpiece):
    quantity: int = Field(..., description="Количество заготовок")


class InputField(BaseModel):
    workpieces: list[GroupWorkpieces] = Field(..., description="Список заготовок")


class OrderField(BaseModel):
    input: InputField
    max_length: int


class BaseBar(BaseModel):
    left_length: int = Field(..., description="Оставшаяся длина в мм")


class CuttedBar(BaseBar):
    used_length: int = Field(default=0, description="Использованная длина")
    workpieces: list[BaseWorkpiece] = Field(
        default=[], description="Необходимые элементы"
        )


class ReadyPattern(BaseModel):
    cutted_bar: CuttedBar
    count: int


class Response(BaseModel):
    patterns: list[ReadyPattern]
    total_whips: int
