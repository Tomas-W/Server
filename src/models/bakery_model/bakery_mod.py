from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, Integer, String, Float, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.extensions import server_db_, logger
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

    search_field: Mapped[str] = mapped_column(Text, nullable=True)

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
        
    def update_search_field(self):
        fields_to_search = [
            self.name.lower(),
            self.category.lower(),
            self.type.lower(),
            self.tags.lower(),
            self.contains.lower(),
        ]
        self.search_field = self._join(fields_to_search)
    
    @staticmethod
    def _join(list_: list[str]) -> str:
        return "|".join(list_)
    
    @staticmethod
    def _split(value: str) -> list[str]:
        return value.split("|") if value else []
    
    @staticmethod
    def _space(value: str) -> str:
        return value.replace("|", " ")
    
    def to_dict(self, *keys) -> dict:
        try:
            all_data = {
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
                "search_field": self._split(self.search_field),
            
                "image": self.image,
            }
            
            if keys:
                return {key: all_data[key] for key in keys if key in all_data}
            return all_data
        except KeyError as e:
            errors = f"KeyError: {e} - {logger.get_log_info()}"
            logger.log.error(errors)
            return {}

    def __repr__(self) -> str:
        return (f"BakeryItem:"
                f" (id={self.id},"
                f" name={self.name},"
                f" category={self.category},"
                f" program={self.program},"
                f" nasa={self.nasa})"
                )

    def cli_repr(self) -> str:
        return f"ID- - - - -{self.id}\n" \
               f"NAME- - - -{self.name}\n" \
               f"CATEGORY- -{self.category}\n" \
               f"NASA- - - -{self.nasa}\n" \
               f"PRICE-- - -{self.price}"
