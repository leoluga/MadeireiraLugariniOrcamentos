# domain/models.py

from dataclasses import dataclass
from enum import Enum
from uuid import uuid4

class UserRole(str, Enum):
    CLIENT = "CLIENT"
    SELLER = "SELLER"
    ADMIN_SELLER = "ADMIN_SELLER"

@dataclass
class Dimensions:
    length: float
    width: float
    height: float

    def volume(self) -> float:
        return self.length * self.width * self.height

class WoodType:
    def __init__(self, name: str, price_per_volume: float):
        self.id = str(uuid4())
        self.name = name
        self.price_per_volume = price_per_volume

class OrcamentoItem:
    """
    Represents a single line item in the Orçamento, which can have multiple pieces
    of a particular wood type with given dimensions.
    """
    def __init__(self, wood_type: WoodType, dimensions: Dimensions, quantity: int):
        self.id = str(uuid4())
        self.wood_type = wood_type
        self.dimensions = dimensions
        self.quantity = quantity
        self.line_price = self._calculate_line_price()  # base line price

    def _calculate_line_price(self) -> float:
        # Each piece price = volume * wood_type price
        # line_price = piece price * quantity
        piece_volume = self.dimensions.volume()
        piece_price = piece_volume * self.wood_type.price_per_volume
        return piece_price * self.quantity

class Orcamento:
    """
    The aggregate root representing an entire quote.
    It can have multiple items (OrcamentoItem).
    """
    def __init__(self):
        self.id = str(uuid4())
        self.items: list[OrcamentoItem] = []
        self.discount = 0.0
        self.final_price = 0.0

    def add_item(self, item: OrcamentoItem):
        self.items.append(item)

    def calculate_base_total(self) -> float:
        return sum(item.line_price for item in self.items)

    def apply_discount(self, discount_value: float, user_role: UserRole):
        if user_role != UserRole.ADMIN_SELLER:
            raise PermissionError("Only Admin Seller can apply discount.")
        # Optionally add some validation if discount exceeds something
        self.discount = discount_value

    def calculate_final_price(self):
        base_total = self.calculate_base_total()
        # Subtract the discount from total
        self.final_price = max(0.0, base_total - self.discount)  # never go below 0

    def confirm(self):
        """
        You might have a confirm/finalize method that
        locks in the final total, triggers domain events, etc.
        """
        self.calculate_final_price()
