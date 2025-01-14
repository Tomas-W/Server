from flask import session
from flask_wtf import FlaskForm
from sqlalchemy import select

from src.extensions import server_db_

from src.models.bakery_model.bakery_mod import BakeryItem
from src.models.bakery_model.bakery_mod_utils import search_bakery_items


def process_bakery_form(form: FlaskForm):
    bakery_items = []
    search_terms = form.search_field.data.split(" ")
    for term in search_terms:
        bakery_items.extend(search_bakery_items(term))

    if form.lactose_free.data:
        bakery_items = [item for item in bakery_items if item.lactose_free]
        
    if form.vegan.data:
        bakery_items = [item for item in bakery_items if item.vegan]
    
    if form.nutri_score.data:
        bakery_items = [item for item in bakery_items if item.nutri_score.lower() == form.nutri_score.data.lower()]

    if not form.min_price.data:
        form.min_price.data = 0
    if not form.max_price.data:
        form.max_price.data = 9.99
    form.min_price.data = str(form.min_price.data).replace(",", ".")
    form.max_price.data = str(form.max_price.data).replace(",", ".")
    min_price = max(0, float(form.min_price.data))
    max_price = min(float(form.max_price.data), 999)
    bakery_items = [item for item in bakery_items if min_price < item.price < max_price]

    return [item.to_dict() for item in bakery_items]


def get_bakery_items_by_column(form: FlaskForm) -> list[BakeryItem] | None:
    columns = ["contains", "may_contain", "price", "nasa"]
    bakery_items = []
    for field in form:
        if field.data and field.name in columns:
            result = server_db_.session.execute(
                select(BakeryItem).filter(getattr(BakeryItem, field.name) == field.data)
            ).scalars().all()
            bakery_items.extend(result)
    return bakery_items


def update_bakery_search_form(form: FlaskForm) -> None:
    input = session.get("bakery_search_input", None)
    if input:
        form.process(data=input)
        form.min_price.data = f"{float(form.min_price.data):.2f}"
        form.max_price.data = f"{float(form.max_price.data):.2f}"
