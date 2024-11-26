from flask import Blueprint, render_template, abort
from flask_login import login_required
from flask import request, redirect, url_for, session

from src.extensions import logger
from src.models.auth_model.auth_mod_utils import admin_required
from src.models.bakery_model.bakery_mod_utils import (
    get_program_items_dicts, get_item_by_id_dict, get_program_ids_and_names,
    get_bakery_programs_info, delete_item_by_id
)
from src.routes.bakery.bakery_forms import (
    BakerySearchForm
)
from src.routes.bakery.bakery_route_utils import (
    process_bakery_form, update_bakery_search_form
)
from config.settings import (
    BAKERY_SEARCH_FORM_TYPE, BAKERY_REFINE_SEARCH_FORM_TYPE,
    PROGRAMS_TEMPLATE, INFO_TEMPLATE, SEARCH_TEMPLATE, SEARCH_REDIRECT,
    ALL_NEWS_REDIRECT, BAKERY_TEMPLATE, DELETE_BAKERY_TEMPLATE,
    PROGRAMS_REDIRECT, DELETE_BAKERY_REDIRECT
)


bakery_bp = Blueprint("bakery", __name__)


@bakery_bp.route("/bakery")
@login_required
def bakery():
    bakery_programs_info = get_bakery_programs_info()
    logger.log.info(bakery_programs_info)
    return render_template(
        BAKERY_TEMPLATE,
        bakery_programs_info=bakery_programs_info,
    )


@bakery_bp.route("/bakery/programs")
@login_required
def programs():
    return render_template(
        PROGRAMS_TEMPLATE,
    )


@bakery_bp.route("/bakery/program/<program>")
@login_required
def program(program: int):
    bakery_items_dicts = get_program_items_dicts(program)
    if not bakery_items_dicts:
        session["error_msg"] = f"Program {program} not in database"
        session["error_user_info"] = f"Program {program} not in database"
        abort(404)

    return render_template(
        PROGRAMS_TEMPLATE,
        bakery_items_dicts=bakery_items_dicts,
    )


@bakery_bp.route("/bakery/info/<id_>")
@login_required
def info(id_: int):
    bakery_item_dict = get_item_by_id_dict(id_)
    if not bakery_item_dict:
        session["error_msg"] = f"Item with ID {id_} not in database"
        session["error_user_info"] = f"Item with ID {id_} not in database"
        abort(404)
        
    # For side panel
    ids_and_names = get_program_ids_and_names(bakery_item_dict["program"])

    return render_template(
        INFO_TEMPLATE,
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
        return redirect(url_for(SEARCH_REDIRECT))
    
    if request.method == "POST":
        if form_type == BAKERY_SEARCH_FORM_TYPE:
            if bakery_search_form.validate_on_submit():
                search_results = process_bakery_form(bakery_search_form)

                session["bakery_search_results"] = search_results
                session["bakery_search_input"] = bakery_search_form.data
                return redirect(url_for(SEARCH_REDIRECT))
        
        elif form_type == BAKERY_REFINE_SEARCH_FORM_TYPE:
            if bakery_search_form.validate_on_submit():
                search_results = session.pop("bakery_search_results", [])
                search_results = process_bakery_form(bakery_search_form)
                
                session["bakery_search_results"] = search_results
                session["bakery_search_input"] = bakery_search_form.data
                return redirect(url_for(SEARCH_REDIRECT))
            
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
        SEARCH_TEMPLATE,
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
        return redirect(url_for(ALL_NEWS_REDIRECT))  # Fallback if no referrer is available


@bakery_bp.route("/bakery/add")
@login_required
@admin_required
def add():
    return render_template(
        BAKERY_TEMPLATE,
    )

@bakery_bp.route("/bakery/delete/<id_>")
@login_required
@admin_required
def delete(id_: int):
    delete_item_by_id(id_)
    referrer = request.headers.get("Referer")
    if referrer:
        return redirect(referrer)
    else:
        return redirect(url_for(PROGRAMS_REDIRECT))
