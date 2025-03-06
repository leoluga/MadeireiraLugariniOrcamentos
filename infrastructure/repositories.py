# infrastructure/repositories.py

from sqlalchemy import Column, String, Float, Integer, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base, SessionLocal
from domain.models import Orcamento, OrcamentoItem, WoodType, Dimensions

class WoodTypeDB(Base):
    __tablename__ = "wood_types"
    id = Column(String, primary_key=True)
    name = Column(String)
    price_per_volume = Column(Float)

class OrcamentoDB(Base):
    __tablename__ = "orcamentos"
    id = Column(String, primary_key=True)
    discount = Column(Float, default=0.0)
    final_price = Column(Float, default=0.0)

    # Relationship to items (one-to-many).
    # Will rely on back_populates or joined relationship in the item table.

class OrcamentoItemDB(Base):
    __tablename__ = "orcamento_items"
    id = Column(String, primary_key=True)
    orcamento_id = Column(String, ForeignKey("orcamentos.id"))
    wood_type_id = Column(String, ForeignKey("wood_types.id"))
    length = Column(Float)
    width = Column(Float)
    height = Column(Float)
    quantity = Column(Integer)
    line_price = Column(Float)

    # If you want a direct relationship in SQLAlchemy, you'd define relationship fields here
    # But for simplicity, we'll do manual queries.

# ---------- Repositories ----------

class WoodTypeRepository:
    def __init__(self, db):
        self.db = db

    def create(self, wood: WoodType):
        record = WoodTypeDB(
            id=wood.id,
            name=wood.name,
            price_per_volume=wood.price_per_volume
        )
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return record

    def get(self, wood_id: str):
        return self.db.query(WoodTypeDB).filter(WoodTypeDB.id == wood_id).first()
    
    def list_all(self):
        return self.db.query(WoodTypeDB).all()

class OrcamentoRepository:
    def __init__(self, db):
        self.db = db

    def create(self, orcamento: Orcamento):
        orc_db = OrcamentoDB(
            id=orcamento.id,
            discount=orcamento.discount,
            final_price=orcamento.final_price
        )
        self.db.add(orc_db)
        self.db.commit()

        # Insert each item
        for item in orcamento.items:
            item_db = OrcamentoItemDB(
                id=item.id,
                orcamento_id=orcamento.id,
                wood_type_id=item.wood_type.id,
                length=item.dimensions.length,
                width=item.dimensions.width,
                height=item.dimensions.height,
                quantity=item.quantity,
                line_price=item.line_price
            )
            self.db.add(item_db)

        self.db.commit()

    def update(self, orcamento: Orcamento):
        # Update orcamento header
        orc_db = self.db.query(OrcamentoDB).filter(OrcamentoDB.id == orcamento.id).first()
        if not orc_db:
            return None
        orc_db.discount = orcamento.discount
        orc_db.final_price = orcamento.final_price
        self.db.commit()
        return orc_db
    
    def update_with_items(self, orcamento: Orcamento):
        """
        Replaces the items of the Orçamento with new data (and updates discount/final_price).
        """
        # 1) Update main orcamento record
        db_orc = self.db.query(OrcamentoDB).filter(OrcamentoDB.id == orcamento.id).first()
        if not db_orc:
            return None

        db_orc.discount = orcamento.discount
        db_orc.final_price = orcamento.final_price
        self.db.commit()

        # 2) Delete old items
        self.db.query(OrcamentoItemDB).filter(OrcamentoItemDB.orcamento_id == orcamento.id).delete()
        self.db.commit()

        # 3) Insert new items from the domain
        for item in orcamento.items:
            item_db = OrcamentoItemDB(
                id=item.id,
                orcamento_id=orcamento.id,
                wood_type_id=item.wood_type.id,
                length=item.dimensions.length,
                width=item.dimensions.width,
                height=item.dimensions.height,
                quantity=item.quantity,
                line_price=item.line_price
            )
            self.db.add(item_db)

        self.db.commit()
        return db_orc

    def get(self, orcamento_id: str) -> Orcamento:
        orc_db = self.db.query(OrcamentoDB).filter(OrcamentoDB.id == orcamento_id).first()
        if not orc_db:
            return None
        # Get items for this orcamento
        items_db = self.db.query(OrcamentoItemDB).filter(OrcamentoItemDB.orcamento_id == orcamento_id).all()

        # Reconstruct domain object
        domain_orc = Orcamento()
        domain_orc.id = orc_db.id
        domain_orc.discount = orc_db.discount
        domain_orc.final_price = orc_db.final_price
        domain_orc.items = []

        for item_db in items_db:
            # You may also fetch the WoodType from DB if needed:
            # wood_record = self.db.query(WoodTypeDB).get(item_db.wood_type_id)
            # wood_domain = WoodType(wood_record.name, wood_record.price_per_volume)
            # wood_domain.id = wood_record.id

            # For demonstration, if we only need the ID & price, do a partial approach:
            wood_record = self.db.query(WoodTypeDB).filter(WoodTypeDB.id == item_db.wood_type_id).first()
            wood_domain = WoodType(wood_record.name, wood_record.price_per_volume)
            wood_domain.id = wood_record.id

            dims = Dimensions(item_db.length, item_db.width, item_db.height)
            line_item = OrcamentoItem(wood_domain, dims, item_db.quantity)
            line_item.id = item_db.id
            # Force the line_price if you want to keep it consistent from DB:
            line_item.line_price = item_db.line_price

            domain_orc.items.append(line_item)
        return domain_orc
    
    def list_all(self) -> list[Orcamento]:
        """
        Return a list of domain Orcamentos.
        For each DB orcamento, we also fetch its items.
        """
        orc_db_list = self.db.query(OrcamentoDB).all()
        domain_orcamentos = []
        for orc_db in orc_db_list:
            domain_orc = Orcamento()
            domain_orc.id = orc_db.id
            domain_orc.discount = orc_db.discount
            domain_orc.final_price = orc_db.final_price
            domain_orc.items = []

            items_db = self.db.query(OrcamentoItemDB).filter(
                OrcamentoItemDB.orcamento_id == orc_db.id
            ).all()

            for item_db in items_db:
                wood_record = self.db.query(WoodTypeDB).filter(
                    WoodTypeDB.id == item_db.wood_type_id
                ).first()
                wood_domain = WoodType(wood_record.name, wood_record.price_per_volume)
                wood_domain.id = wood_record.id

                dims = Dimensions(item_db.length, item_db.width, item_db.height)
                line_item = OrcamentoItem(wood_domain, dims, item_db.quantity)
                line_item.id = item_db.id
                line_item.line_price = item_db.line_price

                domain_orc.items.append(line_item)

            domain_orcamentos.append(domain_orc)

        return domain_orcamentos
    
    def delete(self, orcamento_id: str) -> bool:
        """
        Deletes the orcamento and its items from the DB.
        Returns True if deleted, False if not found.
        """
        db_orc = self.db.query(OrcamentoDB).filter(OrcamentoDB.id == orcamento_id).first()
        if not db_orc:
            return False

        # First delete the items for that orcamento
        self.db.query(OrcamentoItemDB).filter(OrcamentoItemDB.orcamento_id == orcamento_id).delete()

        # Then delete the orcamento record
        self.db.delete(db_orc)
        self.db.commit()
        return True
