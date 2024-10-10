from flask import Blueprint, render_template
from flask_login import current_user
from src.models.bakery_mod import BakeryItem


bakery_bp = Blueprint("bakery", __name__)


@bakery_bp.route("/bakery/programs")
def programs():
    return render_template(
        "bakery/programs.html",
        page="programs",
        username=current_user.username,
    )

@bakery_bp.route("/bakery/program/<program>")
def program(program: int):
    
    bakery_items = BakeryItem.get_all_items(program)

    return render_template(
        "bakery/programs.html",
        page="programs",
        username=current_user.username,
        bakery_items=bakery_items,
    )

@bakery_bp.route("/bakery/info/<id_>")
def info(id_: int):
    bakery_item = BakeryItem.get_item_by_id(id_)

    return render_template(
        "bakery/info.html",
        page="info",
        username=current_user.username,
        bakery_item=bakery_item,
    )

