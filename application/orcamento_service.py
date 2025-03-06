# application/orcamento_service.py

from domain.models import (
    Orcamento,
    OrcamentoItem,
    WoodType,
    Dimensions,
    UserRole
)
from infrastructure.repositories import OrcamentoRepository, WoodTypeRepository

class OrcamentoService:
    def __init__(self, db):
        self.db = db
        self.orc_repo = OrcamentoRepository(db)
        self.wood_repo = WoodTypeRepository(db)

    def create_orcamento(self, items_data: list[dict]) -> Orcamento:
        """
        items_data is a list of dicts like:
        [
          { "wood_id": "...", "length":4, "width":1, "height":3, "quantity":4 },
          { "wood_id": "...", "length":1, "width":1, "height":3, "quantity":2 },
          ...
        ]
        """
        orc = Orcamento()

        for item in items_data:
            wood_rec = self.wood_repo.get(item["wood_id"])
            if not wood_rec:
                raise ValueError(f"Invalid wood type ID: {item['wood_id']}")

            # Convert wood_rec (DB) → domain
            wood_domain = WoodType(wood_rec.name, wood_rec.price_per_volume)
            wood_domain.id = wood_rec.id

            dims = Dimensions(item["length"], item["width"], item["height"])
            orc_item = OrcamentoItem(wood_domain, dims, item["quantity"])

            # Add item to orcamento
            orc.add_item(orc_item)

        # Calculate final price with no discount initially
        orc.calculate_final_price()

        # Persist
        self.orc_repo.create(orc)
        return orc

    def apply_discount(self, orcamento_id: str, discount: float, user_role: UserRole):
        # Retrieve domain object
        orc = self.orc_repo.get(orcamento_id)
        if not orc:
            raise ValueError("Orcamento not found")

        orc.apply_discount(discount, user_role)
        orc.calculate_final_price()

        # Update DB
        self.orc_repo.update(orc)
        return orc

    def get_by_id(self, orcamento_id: str) -> Orcamento:
        return self.orc_repo.get(orcamento_id)

    def list_all(self) -> list[Orcamento]:
        return self.orc_repo.list_all()

    def delete_orcamento(self, orcamento_id: str) -> bool:
        """
        Returns True if deleted, False if not found.
        """
        return self.orc_repo.delete(orcamento_id)
    
    def update_orcamento(self, orcamento_id: str, items_data: list[dict]) -> Orcamento:
        """
        Replace the items of the existing Orçamento with new items_data.
        Recalculate final price, preserve existing discount, update DB.
        """
        # 1. Load the existing Orçamento domain object
        orc = self.orc_repo.get(orcamento_id)
        if not orc:
            raise ValueError("Orcamento not found")

        # 2. Clear existing items in the domain
        #    (We want to replace them entirely)
        orc.items = []

        # 3. Convert new items_data to domain items and add them
        for item_dict in items_data:
            wood_id = item_dict["wood_id"]
            wood_db = self.wood_repo.get(wood_id)
            if not wood_db:
                raise ValueError(f"Invalid wood type ID: {wood_id}")

            # Recreate domain wood
            wood_domain = WoodType(wood_db.name, wood_db.price_per_volume)
            wood_domain.id = wood_db.id

            dims = Dimensions(item_dict["length"], item_dict["width"], item_dict["height"])
            quantity = item_dict["quantity"]

            orc_item = OrcamentoItem(wood_domain, dims, quantity)
            orc.add_item(orc_item)

        # 4. Recalculate final_price (keeping old discount)
        #    The discount is already on the domain object from DB
        orc.calculate_final_price()

        # 5. Pass the updated domain object to the repository
        self.orc_repo.update_with_items(orc)  # We'll define a new repository method
        return orc