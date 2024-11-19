from typing import Optional
from sqlalchemy import select, event

from src.extensions import server_db_
from src.models.bakery_model.bakery_mod import BakeryItem
from src.routes.bakery.bakery_items import get_bakery_dict


def get_program_items_dicts(program: int) -> list[dict]:
    stmt = select(BakeryItem).filter_by(program=program)
    result = server_db_.session.execute(stmt).scalars().all()
    return [item.to_dict() for item in result]


def get_program_ids_and_names(program: int) -> list[dict]:
    stmt = select(BakeryItem).filter_by(program=program)
    items = server_db_.session.execute(stmt).scalars().all()
    return [{"id": item.id, "name": item.name} for item in items]


def get_item_by_id(id_: int) -> Optional[BakeryItem]:
    stmt = select(BakeryItem).filter_by(id=id_)
    return server_db_.session.execute(stmt).scalar_one_or_none()


def get_item_by_id_dict(id_: int) -> Optional[dict]:
    stmt = select(BakeryItem).filter_by(id=id_)
    result = server_db_.session.execute(stmt).scalar_one_or_none()
    return result.to_dict() if result else None


def delete_item_by_id(id_: int) -> None:
    server_db_.session.delete(server_db_.session.get(BakeryItem, id_))
    server_db_.session.commit()


def search_bakery_items(query: str) -> list[BakeryItem]:
    search_term = f"%{query}%"
    stmt = select(BakeryItem).filter(BakeryItem.search_field.like(search_term))
    return server_db_.session.execute(stmt).scalars().all()


def clear_bakery_db() -> None:
    server_db_.session.query(BakeryItem).delete()
    server_db_.session.commit()


@event.listens_for(BakeryItem, 'before_insert')
@event.listens_for(BakeryItem, 'before_update')
def update_search_field(mapper, connection, target):
    target.update_search_field()


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
