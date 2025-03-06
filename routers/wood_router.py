# routers/wood_router.py

from fastapi import APIRouter, Depends, HTTPException, Header
from typing import List, Optional

from schemas.wood_schemas import WoodTypeRead, WoodCreate
from domain.models import WoodType
from infrastructure.repositories import WoodTypeRepository
from .dependencies import get_db

router = APIRouter(
    prefix="/wood",
    tags=["wood"]
)

@router.get("", response_model=List[WoodTypeRead])
def list_wood_types(db=Depends(get_db)):
    """List all wood types."""
    repo = WoodTypeRepository(db)
    return repo.list_all()

@router.get("/{wood_id}", response_model=WoodTypeRead)
def get_wood_type(wood_id: str, db=Depends(get_db)):
    """Get a single wood type by ID."""
    repo = WoodTypeRepository(db)
    record = repo.get(wood_id)
    if not record:
        raise HTTPException(status_code=404, detail="Wood type not found")
    return record

@router.post("", response_model=WoodTypeRead)
def create_wood(
    data: WoodCreate,
    db=Depends(get_db),
    x_user_role: Optional[str] = Header(None)
):
    """
    Create a new Wood entry.
    For demonstration, we only allow "ADMIN_SELLER" or "SELLER" to create wood.
    """
    if x_user_role not in ["ADMIN_SELLER", "SELLER"]:
        raise HTTPException(status_code=403, detail="You are not allowed to create wood.")

    repo = WoodTypeRepository(db)
    wood = WoodType(data.name, data.price_per_volume)
    repo.create(wood)
    return wood

@router.put("/{wood_id}", response_model=WoodTypeRead)
def update_wood(
    wood_id: str,
    data: WoodCreate,
    db=Depends(get_db),
    x_user_role: Optional[str] = Header(None)
):
    """
    Update a wood type (admin only).
    """
    if x_user_role != "ADMIN_SELLER":
        raise HTTPException(status_code=403, detail="Admin only endpoint")

    repo = WoodTypeRepository(db)
    record = repo.get(wood_id)
    if not record:
        raise HTTPException(status_code=404, detail="Wood type not found")

    # Update record
    record.name = data.name
    record.price_per_volume = data.price_per_volume
    db.commit()
    db.refresh(record)
    return record

@router.delete("/{wood_id}")
def delete_wood(
    wood_id: str,
    db=Depends(get_db),
    x_user_role: Optional[str] = Header(None)
):
    """
    Delete a wood type (admin only).
    """
    if x_user_role != "ADMIN_SELLER":
        raise HTTPException(status_code=403, detail="Admin only endpoint")

    repo = WoodTypeRepository(db)
    record = repo.get(wood_id)
    if not record:
        raise HTTPException(status_code=404, detail="Wood type not found")

    db.delete(record)
    db.commit()
    return {"msg": f"Wood '{wood_id}' deleted successfully"}
