from typing import Optional
from sqlalchemy import select

from src.extensions import server_db_
from src.models.bakery_model.bakery_mod import BakeryItem
from src.routes.bakery.bakery_items import get_bakery_dict


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
    """
    Initializer function for cli.
    No internal use.
    """
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
