from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class ObjectModel(BaseModel):
    id: UUID = Field(default_factory=uuid4, alias="_id")
    data: str

    class Config:
        allow_population_by_field_name = True
        schema_extra = {
            "example": {
                "id": "00010203-0405-0607-0809-0a0b0c0d0e0f",
                "data": "My data payload",
            }
        }
