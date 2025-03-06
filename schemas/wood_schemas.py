# schemas/wood_schemas.py

from pydantic import BaseModel, ConfigDict

class WoodTypeRead(BaseModel):
    id: str
    name: str
    price_per_volume: float

    model_config = ConfigDict(from_attributes=True)

class WoodCreate(BaseModel):
    name: str
    price_per_volume: float
