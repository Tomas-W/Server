from flask import Blueprint, render_template
from flask_login import current_user, login_required
from flask import request, redirect, url_for, session

from src.models.bakery_model.bakery_mod import BakeryItem
from src.models.bakery_model.bakery_mod_utils import (
    get_program_items_dicts, get_item_by_id_dict, get_program_ids_and_names
)
from src.routes.bakery.bakery_forms import (
    BakerySearchForm
)
from src.routes.bakery.bakery_route_utils import (
    process_bakery_form
)


bakery_bp = Blueprint("bakery", __name__)


@bakery_bp.route("/bakery/programs")
@login_required
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
@login_required
def info(id_: int):
    bakery_item_dict = get_item_by_id_dict(id_)
    ids_and_names = get_program_ids_and_names(bakery_item_dict["program"])
    for item in ids_and_names:
        print(item["id"])

    return render_template(
        "bakery/info.html",
        page="info",
        username=current_user.username,
        bakery_item_dict=bakery_item_dict,
        ids_and_names=ids_and_names,
    )


@bakery_bp.route("/bakery/search", defaults={"id_": None}, methods=["GET", "POST"])
@bakery_bp.route("/bakery/search/<id_>", methods=["GET", "POST"])
@login_required
def search(id_: int | None = None):
    bakery_search_form = BakerySearchForm()
    
    if request.method == "POST":
        if bakery_search_form.validate_on_submit():
            search_results = process_bakery_form(bakery_search_form)

            session["bakery_search_results"] = search_results
            return redirect(url_for("bakery.search"))
        
        session["bakery_search_errors"] = bakery_search_form.errors
        
        
    bakery_search_errors = session.pop("bakery_search_errors", None)
    
    bakery_search_results_dicts = session.pop("bakery_search_results", [])
    
    bakery_item_dict = None
    if id_:
        bakery_item_dict = get_item_by_id_dict(id_)

    return render_template(
        "bakery/search.html",
        page="search",
        bakery_search_form=bakery_search_form,
        bakery_search_errors=bakery_search_errors,
        bakery_search_results_dicts=bakery_search_results_dicts,
        bakery_item_dict=bakery_item_dict,
    )

@bakery_bp.route("/bakery/zoeken/<search_term>")
@login_required
def zoeken(search_term: str):
    results = BakeryItem.search(search_term)
    bakery_items_dicts = [item.to_dict() for item in results]
    
    return render_template(
        "bakery/programs.html",
        page="programs",
        username=current_user.username,
        bakery_items_dicts=bakery_items_dicts,
    )

