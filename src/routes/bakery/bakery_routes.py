from flask import (
    Blueprint,
    abort,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from flask_login import login_required

from src.models.auth_model.auth_mod_utils import admin_required
from src.models.bakery_model.bakery_mod_utils import (
    delete_item_by_id,
    get_bakery_programs_info,
    get_item_by_id_dict,
    get_program_ids_and_names,
    get_program_items_dicts,
)

from src.routes.bakery.bakery_route_utils import (
    process_bakery_form,
    update_bakery_search_form,
)

from src.routes.bakery.bakery_forms import BakerySearchForm

from src.routes.errors.error_route_utils import Abort404

from config.settings import (
    FORM,
    REDIRECT,
    TEMPLATE,
)

bakery_bp = Blueprint("bakery", __name__)


@bakery_bp.route("/bakery")
@login_required
def bakery():
    bakery_programs_info = get_bakery_programs_info()
    return render_template(
        TEMPLATE.BAKERY,
        bakery_programs_info=bakery_programs_info,
    )


@bakery_bp.route("/bakery/programs")
@login_required
def programs():
    return render_template(
        TEMPLATE.PROGRAMS,
    )


@bakery_bp.route("/bakery/program/<program>")
@login_required
def program(program: int):
    bakery_items_dicts = get_program_items_dicts(program)
    if not bakery_items_dicts:
        description = f"No bakery items found for program {program}"
        raise Abort404(description=description)

    return render_template(
        TEMPLATE.PROGRAMS,
        bakery_items_dicts=bakery_items_dicts,
    )


@bakery_bp.route("/bakery/info/<id_>")
@login_required
def info(id_: int):
    if not isinstance(id_, int):
        description = f"Bakery item with ID {id_} not found"
        raise Abort404(description=description)
    
    bakery_item_dict = get_item_by_id_dict(id_)
    if not bakery_item_dict:
        description = f"Bakery item with ID {id_} not found"
        raise Abort404(description=description)
        
    # For side panel
    ids_and_names = get_program_ids_and_names(bakery_item_dict["program"])

    return render_template(
        TEMPLATE.INFO,
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
        session.pop("bakery_search_results")
        session.pop("bakery_search_input")
        return redirect(url_for(REDIRECT.SEARCH))
    
    if request.method == "POST":
        if form_type == FORM.BAKERY_SEARCH:
            if bakery_search_form.validate_on_submit():
                search_results = process_bakery_form(bakery_search_form)

                session["bakery_search_results"] = search_results
                session["bakery_search_input"] = bakery_search_form.data
                return redirect(url_for(REDIRECT.SEARCH))
        
        elif form_type == FORM.BAKERY_REFINE_SEARCH:
            if bakery_search_form.validate_on_submit():
                search_results = session.pop("bakery_search_results", [])
                search_results = process_bakery_form(bakery_search_form)
                
                session["bakery_search_results"] = search_results
                session["bakery_search_input"] = bakery_search_form.data
                return redirect(url_for(REDIRECT.SEARCH))
            
            session["bakery_search_errors"] = bakery_search_form.errors

    update_bakery_search_form(bakery_search_form)
    
    bakery_search_errors = session.pop("bakery_search_errors", None)
    bakery_search_results_dicts = session.get("bakery_search_results", None)
    if bakery_search_results_dicts:
        bakery_search_form.submit.label.text = "Refine"
        
    bakery_item_dict = None
    if id_:
        bakery_item_dict = get_item_by_id_dict(id_)
    
    return render_template(
        TEMPLATE.SEARCH,
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
        return redirect(url_for(REDIRECT.ALL_NEWS))  # Fallback if no referrer is available


@bakery_bp.route("/bakery/add")
@admin_required
@login_required
def add():
    return render_template(
        TEMPLATE.BAKERY,
    )

@bakery_bp.route("/bakery/delete/<id_>")
@admin_required
@login_required
def delete(id_: int):
    delete_item_by_id(id_)
    referrer = request.headers.get("Referer")
    if referrer:
        return redirect(referrer)
    else:
        return redirect(url_for(REDIRECT.PROGRAMS))
