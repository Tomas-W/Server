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

@bakery_bp.route("/bakery/programs/<program>")
def program(program: int):
    
    bakery_items = BakeryItem.get_all_items(program)
    bakery_images = [bakery_item.image for bakery_item in bakery_items]
    print(bakery_images)
    
    return render_template(
        "bakery/programs.html",
        page="programs",
        username=current_user.username,
        bakery_images=bakery_images,
    )


