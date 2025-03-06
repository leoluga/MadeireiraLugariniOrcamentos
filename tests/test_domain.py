# tests/test_domain.py

import pytest
from domain.models import Orcamento, OrcamentoItem, WoodType, Dimensions, UserRole

def test_orcamento_item_price():
    wood = WoodType(name="TestWood", price_per_volume=10.0)
    dims = Dimensions(length=2, width=1, height=1)
    item = OrcamentoItem(wood, dims, quantity=5)
    # volume = 2*1*1 = 2
    # price per piece = 2 * 10 = 20
    # total line_price = 20 * 5 = 100
    assert item.line_price == 100

def test_apply_discount_only_admin():
    orc = Orcamento()
    wood = WoodType(name="TestWood", price_per_volume=10.0)
    dims = Dimensions(length=1, width=1, height=1)
    item = OrcamentoItem(wood, dims, quantity=2)
    orc.add_item(item)

    orc.calculate_final_price()  # base_total = 2 * 1 * 1 * 10 = 20

    # Non-admin tries discount => should raise PermissionError
    with pytest.raises(PermissionError):
        orc.apply_discount(5.0, user_role=UserRole.SELLER)

    # Admin can apply discount
    orc.apply_discount(5.0, user_role=UserRole.ADMIN_SELLER)
    orc.calculate_final_price()
    assert orc.final_price == 20 - 5  # => 15
