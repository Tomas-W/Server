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
    bakery_images = [item.image for item in bakery_items]
    for i, image in enumerate(bakery_images):
        print(f"{i+1}: {image}")
    return render_template(
        "bakery/programs.html",
        page="programs",
        username=current_user.username,
        bakery_images=bakery_images,
    )
