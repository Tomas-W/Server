from flask import Blueprint, render_template

bakery_bp = Blueprint("bakery", __name__)


@bakery_bp.route("/bakery/programs")
def bakery_programs():
    return render_template(
        "bakery/programs.html",
        page="programs",
    )

