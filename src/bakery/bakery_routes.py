from flask import Blueprint, render_template
from flask_login import current_user
from src.models.bakery_mod import get_program_items_dicts, get_item_by_id_dict


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
    
    bakery_items_dicts = get_program_items_dicts(program)

    return render_template(
        "bakery/programs.html",
        page="programs",
        username=current_user.username,
        bakery_items_dicts=bakery_items_dicts,
    )

@bakery_bp.route("/bakery/info/<id_>")
def info(id_: int):
    bakery_item_dict = get_item_by_id_dict(id_)

    return render_template(
        "bakery/info.html",
        page="info",
        username=current_user.username,
        bakery_item_dict=bakery_item_dict,
    )

