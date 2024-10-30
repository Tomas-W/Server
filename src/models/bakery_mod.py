from datetime import datetime
from typing import Optional

from sqlalchemy import select, Boolean, Integer, String, Float, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from src.extensions import server_db_

from src.bakery.bakery_items import get_bakery_dict
from config.settings import CET


class BakeryItem(server_db_.Model):
    """
    Stores the BakeryItem data.

    - ID (int): Identifier [Primary Key]
    - NAME (str): Name of the item [Required]
    - CATEGORY (str): Category of the item [Required]
    - PROGRAM (int): Baking program number [Required]
    - NASA (int): NASA code [Required]
    - PRICE (float): Price of the item [Required]
    
    - VEGAN (bool): Indicates if the item is vegan [Default: False]
    - LACTOSE_FREE (bool): Indicates if the item is lactose-free [Default: False]
    - NUTRI_SCORE (str): Nutritional score [Required]
    
    - TYPE (str): Type of the item [Required]
    - TAGS (str): Tags associated with the item [Required]
    - PACKAGE_TYPE (str): Type of package [Optional]
    - PER_PACKAGE (str): Quantity per package [Optional]
    - RACK_TYPE (str): Type of baking rack [Optional]
    - PER_RACK (str): Quantity per rack [Optional]
    - DEFROST_TIME (str): Defrost time [Optional]
    - COOLDOWN_TIME (str): Cooldown time [Optional]
    - MAKE_HALVES (bool): Indicates if halves may be made [Optional]
    
    - CONTAINS (str): Allergens contained in the item [Required]
    - MAY_CONTAIN (str): Allergens that may be present [Required]
    
    - IMAGE (str): Path to the item's image [Optional]
    
    - CREATED_AT (datetime): Timestamp of item creation [Default] [CET]
    - UPDATED_AT (datetime): Timestamp of last update [Default] [CET]
    """
    __tablename__ = "bakery_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(75), nullable=False)
    category: Mapped[str] = mapped_column(String(75), nullable=False)
    program: Mapped[int] = mapped_column(Integer, nullable=False)
    nasa: Mapped[int] = mapped_column(Integer, nullable=False)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    
    vegan: Mapped[bool] = mapped_column(Boolean, default=False)
    lactose_free: Mapped[bool] = mapped_column(Boolean, default=False)
    nutri_score: Mapped[str] = mapped_column(String(1), nullable=False)
    
    type: Mapped[str] = mapped_column(String(225), nullable=False)
    tags: Mapped[str] = mapped_column(String(225), nullable=False)
    package_type: Mapped[Optional[str]] = mapped_column(String(75))
    per_package: Mapped[Optional[str]] = mapped_column(String(75))
    rack_type: Mapped[Optional[str]] = mapped_column(String(75))
    per_rack: Mapped[Optional[str]] = mapped_column(String(75))
    defrost_time: Mapped[Optional[str]] = mapped_column(String(75))
    cooldown_time: Mapped[Optional[str]] = mapped_column(String(75))
    make_halves: Mapped[Optional[bool]] = mapped_column(Boolean)
    
    contains: Mapped[str] = mapped_column(String(255), nullable=False)
    may_contain: Mapped[str] = mapped_column(String(255), nullable=False)
    
    image: Mapped[str] = mapped_column(String(255), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime,
                                                 default=lambda: datetime.now(CET))
    updated_at: Mapped[datetime] = mapped_column(DateTime,
                                                 default=lambda: datetime.now(CET),
                                                 onupdate=lambda: datetime.now(CET))

    def __init__(self, name: str, category: str, program: int, nasa: int, price: float,
                 type: list[str], tags: list[str], package_type: Optional[str],
                 per_package: Optional[str], rack_type: Optional[str],
                 per_rack: Optional[str], defrost_time: Optional[str],
                 cooldown_time: str, make_halves: Optional[bool], vegan: bool,
                 lactose_free: bool, nutri_score: str, contains: list[str],
                 may_contain: list[str], image: str):
        self.name = name
        self.category = category
        self.program = program
        self.nasa = nasa
        self.price = price
        
        self.vegan = vegan
        self.lactose_free = lactose_free
        self.nutri_score = nutri_score
        
        self.type = self._join(type)
        self.tags = self._join(tags)
        self.package_type = package_type
        self.per_package = per_package
        self.rack_type = rack_type
        self.per_rack = per_rack
        self.defrost_time = defrost_time
        self.cooldown_time = cooldown_time
        self.make_halves = make_halves
        
        self.contains = self._join(contains)
        self.may_contain = self._join(may_contain)
        
        self.image = image

    @staticmethod
    def _join(list_: list[str]) -> str:
        return "|".join(list_)
    
    @staticmethod
    def _split(value: str) -> list[str]:
        return value.split("|") if value else []
    
    @staticmethod
    def _space(value: str) -> str:
        return value.replace("|", " ")
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "category": self.category,
            "program": self.program,
            "nasa": self.nasa,
            "price": self.price,
            
            "vegan": self.vegan,
            "lactose_free": self.lactose_free,
            "nutri_score": self.nutri_score,
            
            "type": self._space(self.type),
            "tags": self._split(self.tags),
            "package_type": self.package_type,
            "per_package": self.per_package,
            "rack_type": self.rack_type,
            "per_rack": self.per_rack,
            "defrost_time": self.defrost_time,
            "cooldown_time": self.cooldown_time,
            "make_halves": self.make_halves,
            
            "contains": self._split(self.contains),
            "may_contain": self._split(self.may_contain),
            
            "image": self.image,
        }
    
    def __repr__(self) -> str:
        return (f"BakeryItem:"
                f" (id={self.id},"
                f" name={self.name},"
                f" category={self.category},"
                f" program={self.program},"
                f" nasa={self.nasa})"
                )


def get_program_items_dicts(program: int) -> list[dict]:
    result = server_db_.session.execute(
        select(BakeryItem).filter_by(program=program)
    ).scalars().all()
    return [item.to_dict() for item in result]


def get_item_by_id(id_: int) -> Optional[BakeryItem]:
    result = server_db_.session.execute(
            select(BakeryItem).filter_by(id=id_)
    ).scalar_one_or_none()
    return result


def get_item_by_id_dict(id_: int) -> Optional[dict]:
    result = server_db_.session.execute(
            select(BakeryItem).filter_by(id=id_)
    ).scalar_one_or_none()
    return result.to_dict()


def delete_item_by_id(id_: int) -> None:
    server_db_.session.delete(server_db_.session.get(BakeryItem, id_))
    server_db_.session.commit()

def clear_bakery_db() -> None:
    server_db_.session.query(BakeryItem).delete()
    server_db_.session.commit()


def _init_bakery() -> bool | None:
    if not server_db_.session.query(BakeryItem).count():
        bakery_dict = get_bakery_dict()
        for item_name, item_details in bakery_dict.items():
            bakery_item = BakeryItem(
                name=item_name,
                category=item_details["category"],
                program=item_details["program"],
                nasa=item_details["nasa"],
                price=item_details["price"],
                type=item_details["type"],
                tags=item_details["tags"],
                package_type=item_details["package_type"],
                per_package=item_details["per_package"],
                rack_type=item_details["rack_type"],
                per_rack=item_details["per_rack"],
                defrost_time=item_details["defrost_time"],
                cooldown_time=item_details["cooldown_time"],
                make_halves=item_details["make_halves"],
                vegan=item_details["vegan"],
                lactose_free=item_details["lactose_free"],
                nutri_score=item_details["nutri_score"],
                contains=item_details["contains"],
                may_contain=item_details["may_contain"],
                image=item_details["image"]
            )
            server_db_.session.add(bakery_item)
        server_db_.session.commit()
        return True
    
    return None
