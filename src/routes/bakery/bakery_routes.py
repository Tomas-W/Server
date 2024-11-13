from flask import Blueprint, render_template
from flask_login import current_user, login_required
from flask import request, redirect, url_for, session

from src.models.bakery_model.bakery_mod_utils import (
    get_program_items_dicts, get_item_by_id_dict, get_program_ids_and_names
)
from src.routes.bakery.bakery_forms import (
    BakerySearchForm
)
from src.routes.bakery.bakery_route_utils import (
    process_bakery_form
)
from config.settings import (
    BAKERY_SEARCH_FORM_TYPE, BAKERY_REFINE_SEARCH_FORM_TYPE
)


bakery_bp = Blueprint("bakery", __name__)


@bakery_bp.route("/bakery/programs")
@login_required
def programs():
    return render_template(
        "bakery/programs.html",
        page=["programs"],
    )

@bakery_bp.route("/bakery/program/<program>")
def program(program: int):
    
    bakery_items_dicts = get_program_items_dicts(program)

    return render_template(
        "bakery/programs.html",
        page=["programs"],
        bakery_items_dicts=bakery_items_dicts,
    )

@bakery_bp.route("/bakery/info/<id_>")
@login_required
def info(id_: int):
    bakery_item_dict = get_item_by_id_dict(id_)
    ids_and_names = get_program_ids_and_names(bakery_item_dict["program"])

    return render_template(
        "bakery/info.html",
        page=["info"],
        bakery_item_dict=bakery_item_dict,
        ids_and_names=ids_and_names,
    )


@bakery_bp.route("/bakery/search", defaults={"id_": None}, methods=["GET", "POST"])
@bakery_bp.route("/bakery/search/<id_>", methods=["GET", "POST"])
@login_required
def search(id_: int | None = None, reset: bool = False):
    bakery_search_form = BakerySearchForm()
    form_type = request.form.get("form_type")

    reset = request.args.get("reset")
    if reset:
        session.pop("bakery_search_results", None)
        session.pop("bakery_search_input", None)
        return redirect(url_for("bakery.search"))
    
    if request.method == "POST":
        if form_type == BAKERY_SEARCH_FORM_TYPE:
            if bakery_search_form.validate_on_submit():
                search_results = process_bakery_form(bakery_search_form)

                session["bakery_search_results"] = search_results
                session["bakery_search_input"] = bakery_search_form.data
                return redirect(url_for("bakery.search"))
        
        elif form_type == BAKERY_REFINE_SEARCH_FORM_TYPE:
            if bakery_search_form.validate_on_submit():
                search_results = session.pop("bakery_search_results", [])
                search_results = process_bakery_form(bakery_search_form)
                session["bakery_search_results"] = search_results
                session["bakery_search_input"] = bakery_search_form.data
                return redirect(url_for("bakery.search"))
            
            session["bakery_search_errors"] = bakery_search_form.errors
    
    bakery_search_input = session.get("bakery_search_input", None)
    if bakery_search_input:
        bakery_search_form.process(data=bakery_search_input)
        bakery_search_form.min_price.data = f"{float(bakery_search_form.min_price.data):.2f}"
        bakery_search_form.max_price.data = f"{float(bakery_search_form.max_price.data):.2f}"
    
    bakery_search_errors = session.pop("bakery_search_errors", None)
    bakery_search_results_dicts = session.get("bakery_search_results", None)
    if bakery_search_results_dicts:
        bakery_search_form.submit.label.text = "Refine"
        
    bakery_item_dict = None
    if id_:
        bakery_item_dict = get_item_by_id_dict(id_)

    return render_template(
        "bakery/search.html",
        page=["search"],
        bakery_search_form=bakery_search_form,
        bakery_search_results_dicts=bakery_search_results_dicts,
        bakery_search_errors=bakery_search_errors,
        
        bakery_item_dict=bakery_item_dict,
    )


@bakery_bp.route("/bakery/health/<filename>")
@login_required
def bakery_health(filename):
    referrer = request.headers.get("Referer")
    if referrer:
        return redirect(referrer)
    else:
        return redirect(url_for("news.all_news"))  # Fallback if no referrer is available

