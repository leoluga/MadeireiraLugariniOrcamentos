# tests/test_application.py

import pytest
from application.orcamento_service import OrcamentoService
from domain.models import WoodType, UserRole
from infrastructure.repositories import WoodTypeRepository

def test_create_orcamento(db_session):
    wood_repo = WoodTypeRepository(db_session)
    wood = WoodType("TestWood", 12.5)
    wood_repo.create(wood)

    service = OrcamentoService(db_session)
    items_data = [
        {
            "wood_id": wood.id,
            "length": 2,
            "width": 1,
            "height": 1,
            "quantity": 4
        }
    ]
    orc = service.create_orcamento(items_data)
    assert orc.id is not None
    assert len(orc.items) == 1
    #  volume = 2*1*1 = 2 => line price=2*12.5=25 => total=25*4=100
    assert orc.final_price == 2 * 12.5 * 4

def test_apply_discount(db_session):
    wood_repo = WoodTypeRepository(db_session)
    service = OrcamentoService(db_session)

    # Insert a wood
    w = WoodType("Oak", 8.0)
    wood_repo.create(w)

    # Create orcamento
    data = [
        {"wood_id": w.id, "length":1, "width":1, "height":2, "quantity":2}
    ]
    orc = service.create_orcamento(data)
    base_total = orc.final_price

    # Admin discount => OK
    updated = service.apply_discount(orc.id, discount=5.0, user_role=UserRole.ADMIN_SELLER)
    assert updated.final_price == base_total - 5.0

    # Non-admin => should raise PermissionError from domain
    with pytest.raises(PermissionError):
        service.apply_discount(orc.id, 5.0, UserRole.SELLER)
