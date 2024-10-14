from datetime import datetime
from typing import Optional, List

from sqlalchemy import Boolean, Integer, String, Float, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import select
from sqlalchemy.ext.declarative import declarative_base

from config.settings import CET
from src.extensions import server_db_


class BakeryItem(server_db_.Model):
    """
    Stores the bakery item data and their attributes.

    - ID: Unique identifier for the item
    - NAME: Name of the item
    - CATEGORY: Category of the item
    - PROGRAM: Program number
    - NASA: NASA code
    - PRICE: Price of the item
    - TYPE: Type of the item
    - TAGS: Tags associated with the item
    - RACK_TYPE: Type of rack
    - PER_RACK: Quantity per rack
    - DEFROST_TIME: Defrost time
    - COOLDOWN_TIME: Cooldown time
    - MAKE_HALVES: Indicates if halves can be made
    - VEGAN: Boolean indicating if the item is vegan
    - CONTAINS: Ingredients contained in the item
    - MAY_CONTAIN: Possible allergens
    - IMAGE: Path to the item's image
    """
    __tablename__ = "bakery_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(75), nullable=False)
    category: Mapped[str] = mapped_column(String(75), nullable=False)
    program: Mapped[int] = mapped_column(Integer, nullable=False)
    nasa: Mapped[int] = mapped_column(Integer, nullable=False)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    type: Mapped[str] = mapped_column(String(225), nullable=False)
    tags: Mapped[str] = mapped_column(String(225), nullable=False)
    package_type: Mapped[Optional[str]] = mapped_column(String(75))
    per_package: Mapped[Optional[str]] = mapped_column(String(75))
    rack_type: Mapped[Optional[str]] = mapped_column(String(75))
    per_rack: Mapped[Optional[str]] = mapped_column(String(75))
    defrost_time: Mapped[Optional[str]] = mapped_column(String(75))
    cooldown_time: Mapped[Optional[str]] = mapped_column(String(75))
    make_halves: Mapped[Optional[bool]] = mapped_column(Boolean)
    vegan: Mapped[bool] = mapped_column(Boolean, default=False)
    lactose_free: Mapped[bool] = mapped_column(Boolean, default=False)
    nutri_score: Mapped[str] = mapped_column(String(1), nullable=False)
    contains: Mapped[str] = mapped_column(String(255), nullable=False)
    may_contain: Mapped[str] = mapped_column(String(255), nullable=False)
    image: Mapped[str] = mapped_column(String(255), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime,
                                                 default=lambda: datetime.now(CET))
    updated_at: Mapped[datetime] = mapped_column(DateTime,
                                                 default=lambda: datetime.now(CET),
                                                 onupdate=lambda: datetime.now(CET))

    def __init__(self, name: str, category: str, program: int, nasa: int, price: float,
                 type: str, tags: str, package_type: Optional[str],
                 per_package: Optional[str], rack_type: Optional[str],
                 per_rack: Optional[str], defrost_time: Optional[str],
                 cooldown_time: str, make_halves: Optional[bool], vegan: bool,
                 lactose_free: bool, nutri_score: str, contains: str,
                 may_contain: str, image: str):
        self.name = name
        self.category = category
        self.program = program
        self.nasa = nasa
        self.price = price
        self.type = type
        self.tags = tags
        self.package_type = package_type
        self.per_package = per_package
        self.rack_type = rack_type
        self.per_rack = per_rack
        self.defrost_time = defrost_time
        self.cooldown_time = cooldown_time
        self.make_halves = make_halves
        self.vegan = vegan
        self.lactose_free = lactose_free
        self.nutri_score = nutri_score
        self.contains = contains
        self.may_contain = may_contain
        self.image = image

    def __repr__(self):
        return (f"BakeryItem: "
                f"(id={self.id},"
                f" name={self.name},"
                f" category={self.category},"
                f" program={self.program},"
                f" nasa={self.nasa},")
    
    @staticmethod
    def get_all_items(program: int):
        result = server_db_.session.execute(
            select(BakeryItem).filter_by(program=program)
        ).scalars().all()
        return result
    
    @staticmethod
    def get_item_by_id(id_: int):
        result = server_db_.session.execute(
            select(BakeryItem).filter_by(id=id_)
        ).scalar_one_or_none()
        return result
