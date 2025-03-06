# schemas/orcamento_schemas.py

from pydantic import BaseModel, ConfigDict
from typing import List
from domain.models import UserRole

class ItemData(BaseModel):
    wood_id: str
    length: float
    width: float
    height: float
    quantity: int

class CreateOrcamentoRequest(BaseModel):
    items: List[ItemData]

class CreateOrcamentoResponse(BaseModel):
    orcamento_id: str
    final_price: float

class DiscountRequest(BaseModel):
    orcamento_id: str
    discount: float
    user_role: UserRole

class UpdateOrcamentoRequest(BaseModel):
    """Schema for updating an existing Orçamento (replacing its items)."""
    items: List[ItemData]

class OrcamentoItemRead(BaseModel):
    id: str
    wood_type_id: str
    wood_name: str
    length: float
    width: float
    height: float
    quantity: int
    line_price: float

    model_config = ConfigDict(from_attributes=True)

class OrcamentoRead(BaseModel):
    id: str
    discount: float
    final_price: float
    items: List[OrcamentoItemRead]
