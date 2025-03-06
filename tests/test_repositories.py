# tests/test_repositories.py

from infrastructure.repositories import WoodTypeRepository, OrcamentoRepository
from domain.models import WoodType, Orcamento, OrcamentoItem, Dimensions

def test_wood_repository(db_session):
    repo = WoodTypeRepository(db_session)
    wood = WoodType(name="Pine", price_per_volume=5.0)
    repo.create(wood)

    # Check it was inserted
    fetched = repo.get(wood.id)
    assert fetched is not None
    assert fetched.name == "Pine"
    assert fetched.price_per_volume == 5.0

def test_orcamento_repository_create_get(db_session):
    wood_repo = WoodTypeRepository(db_session)
    orc_repo = OrcamentoRepository(db_session)

    # Insert a wood
    wood = WoodType("Cedar", 10.0)
    wood_repo.create(wood)

    # Build domain orcamento
    orc = Orcamento()
    dims = Dimensions(2,2,1)
    item = OrcamentoItem(wood, dims, quantity=3)
    orc.add_item(item)
    orc.calculate_final_price()

    # Save to DB
    orc_repo.create(orc)
    fetched = orc_repo.get(orc.id)

    assert fetched is not None
    assert fetched.id == orc.id
    assert len(fetched.items) == 1
    assert fetched.items[0].wood_type.name == "Cedar"

def test_orcamento_repository_delete(db_session):
    wood_repo = WoodTypeRepository(db_session)
    orc_repo = OrcamentoRepository(db_session)

    wood = WoodType("Balsa", 2.0)
    wood_repo.create(wood)

    orc = Orcamento()
    dims = Dimensions(1,1,2)
    item = OrcamentoItem(wood, dims, quantity=2)
    orc.add_item(item)
    orc.calculate_final_price()
    orc_repo.create(orc)

    # Confirm it exists
    fetched = orc_repo.get(orc.id)
    assert fetched is not None

    # Delete
    success = orc_repo.delete(orc.id)
    assert success

    # Confirm it's gone
    fetched_after = orc_repo.get(orc.id)
    assert fetched_after is None
