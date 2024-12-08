import os
from pprint import pformat
from flask import (
    Blueprint, render_template, request, session, flash, redirect, url_for
)
from flask_login import current_user
from src.models.schedule_model.schedule_mod import Schedule
from config.settings import (
    SCHEDULE_PERSONAL_TEMPLATE, SCHEDULE_REQUEST_FORM_TYPE
)
from src.extensions import logger
from src.routes.schedule.schedule_route_utils import (
    get_requested_date, get_personal_schedule_dicts, update_schedule,
    get_five_weeks_dates
)
from src.models.auth_model.auth_mod_utils import (
    start_verification_process, confirm_authentication_token,
    delete_authentication_token
)
from src.routes.schedule.schedule_forms import ScheduleRequestForm
from src.models.schedule_model.schedule_mod_utils import update_employee
from config.settings import (
    EMPLOYEE_VERIFICATION, EMPLOYEE_VERIFICATION_SEND_MSG, SCHEDULE_REDIRECT,
    UNEXPECTED_ERROR_MSG, EMPLOYEE_VERIFIED_MSG
)

schedule_bp = Blueprint("schedule", __name__)


@schedule_bp.route("/schedule/personal", methods=["GET", "POST"])
@schedule_bp.route("/schedule/<date>", methods=["GET", "POST"])
def personal(date: str = None):
    schedule_reqest_form = ScheduleRequestForm()
    schedule_reqest_form.email.data = current_user.email
    form_type = request.form.get("form_type")
    
    if request.method == "POST":
        if form_type == SCHEDULE_REQUEST_FORM_TYPE:
            if schedule_reqest_form.validate_on_submit():
                session["employee_name"] = schedule_reqest_form.name.data
                start_verification_process(email=schedule_reqest_form.email.data,
                                           token_type=EMPLOYEE_VERIFICATION)
                flash(EMPLOYEE_VERIFICATION_SEND_MSG)
                session["flash_type"] = "employee_verification"
                return redirect(url_for(SCHEDULE_REDIRECT,
                                        _anchor="schedule-wrapper"))
                
            session["schedule_request_errors"] = schedule_reqest_form.errors
    
    requested_date = get_requested_date(date)
    requested_schedule = Schedule.query.filter_by(date=requested_date).first()
    requested_schedule_dict = requested_schedule.date_to_dict() if requested_schedule else {}
    
    personal_schedule_dicts = get_personal_schedule_dicts()
    
    schedule_request_errors = session.get("schedule_request_errors", None)   
    flash("Test flash message")
    return render_template(
        SCHEDULE_PERSONAL_TEMPLATE,
        display_table=True,
        schedule=requested_schedule_dict,
        schedule_request_form=schedule_reqest_form,
        schedule_request_errors=schedule_request_errors,
        personal_schedule_dicts=personal_schedule_dicts
        )


@schedule_bp.route("/schedule/personal/calendar", methods=["POST"])
def calendar():
    pass


@schedule_bp.route("/schedule/verify-employee/<token>", methods=["GET"])
def verify_employee(token):    
    email = confirm_authentication_token(token, EMPLOYEE_VERIFICATION)
    employee_name = session.pop("employee_name", None)
    
    if not employee_name:
        logger.log.error(f"Employee name not in session for email: {email}")
        flash(UNEXPECTED_ERROR_MSG)
        return redirect(url_for(SCHEDULE_REDIRECT))
    
    if not email:
        logger.log.error(f"Email not confirmed for token: {token}")
        flash(UNEXPECTED_ERROR_MSG)
        return redirect(url_for(SCHEDULE_REDIRECT))
    
    if not update_employee(employee_name, email):
        flash(UNEXPECTED_ERROR_MSG)
        logger.log.error(f"Failed to update employee {employee_name} with email {email}")
        return redirect(url_for(SCHEDULE_REDIRECT))
    
    delete_authentication_token(EMPLOYEE_VERIFICATION, token)
    flash(EMPLOYEE_VERIFIED_MSG)
    return redirect(url_for(SCHEDULE_REDIRECT))
