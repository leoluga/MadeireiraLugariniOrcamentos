# routers/orcamento_router.py

from fastapi import APIRouter, Depends, HTTPException, Header
from typing import List, Optional

from domain.models import UserRole
from application.orcamento_service import OrcamentoService
from schemas.orcamento_schemas import (
    CreateOrcamentoRequest,
    CreateOrcamentoResponse,
    DiscountRequest,
    OrcamentoRead,
    OrcamentoItemRead,
    UpdateOrcamentoRequest
)
from .dependencies import get_db

router = APIRouter(
    prefix="/orcamento",
    tags=["orcamento"]
)

@router.get("", response_model=List[OrcamentoRead])
def list_orcamentos(db=Depends(get_db)):
    service = OrcamentoService(db)
    domain_orcamentos = service.list_all()
    return [convert_orcamento_to_read_schema(o) for o in domain_orcamentos]

@router.get("/{orcamento_id}", response_model=OrcamentoRead)
def get_orcamento(orcamento_id: str, db=Depends(get_db)):
    service = OrcamentoService(db)
    domain_orc = service.get_by_id(orcamento_id)
    if not domain_orc:
        raise HTTPException(status_code=404, detail="Orcamento not found")
    return convert_orcamento_to_read_schema(domain_orc)

@router.post("", response_model=CreateOrcamentoResponse)
def create_orcamento(req: CreateOrcamentoRequest, db=Depends(get_db)):
    """
    Create an Orçamento with multiple items.
    Anyone can create for demonstration. 
    (In reality, you might only let SELLER or ADMIN_SELLER create it.)
    """
    service = OrcamentoService(db)
    try:
        orc = service.create_orcamento([item.model_dump() for item in req.items])
        return CreateOrcamentoResponse(
            orcamento_id=orc.id,
            final_price=orc.final_price
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/discount")
def apply_discount(req: DiscountRequest, db=Depends(get_db)):
    """
    Apply a discount to an existing Orçamento.
    Only an ADMIN_SELLER can do this (enforced by domain rule).
    """
    service = OrcamentoService(db)
    try:
        orc = service.apply_discount(req.orcamento_id, req.discount, req.user_role)
        return {
            "id": orc.id,
            "final_price": orc.final_price,
            "discount_applied": orc.discount
        }
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/{orcamento_id}", response_model=OrcamentoRead)
def update_orcamento(
    orcamento_id: str, 
    req: UpdateOrcamentoRequest,
    db=Depends(get_db),
    x_user_role: str = Header(None)
):
    """
    Full update: replace existing items with new items.
    Preserves existing discount.
    """
    if x_user_role not in ["SELLER", "ADMIN_SELLER"]:
        raise HTTPException(status_code=403, detail="Only sellers can update orcamentos.")
    
    service = OrcamentoService(db)
    try:
        updated_orc = service.update_orcamento(orcamento_id, [item.dict() for item in req.items])
        return convert_orcamento_to_read_schema(updated_orc)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{orcamento_id}")
def delete_orcamento(
    orcamento_id: str,
    db=Depends(get_db),
    x_user_role: Optional[str] = Header(None)
):
    """
    Delete an Orçamento (admin only).
    """
    if x_user_role != "ADMIN_SELLER":
        raise HTTPException(status_code=403, detail="Admin only endpoint")

    service = OrcamentoService(db)
    deleted = service.delete_orcamento(orcamento_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Orcamento not found or already deleted")
    return {"msg": f"Orcamento '{orcamento_id}' deleted successfully"}

def convert_orcamento_to_read_schema(domain_orc):
    items_read = []
    for item in domain_orc.items:
        items_read.append(
            OrcamentoItemRead(
                id=item.id,
                wood_type_id=item.wood_type.id,
                wood_name=item.wood_type.name,
                length=item.dimensions.length,
                width=item.dimensions.width,
                height=item.dimensions.height,
                quantity=item.quantity,
                line_price=item.line_price,
            )
        )
    return OrcamentoRead(
        id=domain_orc.id,
        discount=domain_orc.discount,
        final_price=domain_orc.final_price,
        items=items_read
    )
