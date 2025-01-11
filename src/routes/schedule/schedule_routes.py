from datetime import timedelta, datetime
from flask import (
    Blueprint, render_template, request, session, flash, redirect, url_for
)
from flask_login import login_required, current_user
from src.models.schedule_model.schedule_mod import Schedule
from config.settings import (
    SCHEDULE_PERSONAL_TEMPLATE, SCHEDULE_CALENDAR_TEMPLATE,
    SCHEDULE_REQUEST_FORM_TYPE
)
from src.extensions import logger
from src.routes.schedule.schedule_route_utils import (
    get_requested_date, get_personal_schedule_dicts, get_calendar_dates,
    get_prev_month_days, get_next_month_days, get_calendar_week_numbers,
    get_shortened_week_days
)
from src.models.auth_model.auth_mod_utils import (
    start_verification_process, confirm_authentication_token,
    delete_authentication_token, employee_required
)
from src.routes.schedule.schedule_forms import (
    ScheduleRequestForm, CalendarForm
)
from src.models.schedule_model.schedule_mod_utils import (
    activate_employee, get_calendar_on_duty_days
)
from src.utils.schedule import _week_from_date, _now
from config.settings import (
    EMPLOYEE_VERIFICATION, EMPLOYEE_VERIFICATION_SEND_MSG, SCHEDULE_REDIRECT,
    EMPLOYEE_VERIFIED_MSG, EMPLOYEE_NOT_FOUND_MSG, SESSION_ERROR_MSG,
    AUTHENTICATION_LINK_ERROR_MSG
)

schedule_bp = Blueprint("schedule", __name__)




@schedule_bp.route("/schedule/personal", methods=["GET", "POST"])
@schedule_bp.route("/schedule/<date>", methods=["GET"])
@employee_required
@login_required
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
    requested_schedule = Schedule.query.filter_by(date=requested_date).one_or_none()
    prev_date = requested_date - timedelta(days=1)
    prev_date_schedule = Schedule.query.filter_by(date=prev_date).one_or_none()
    next_date = requested_date + timedelta(days=1)
    next_date_schedule = Schedule.query.filter_by(date=next_date).one_or_none()
    may_prev = prev_date_schedule is not None
    may_next = next_date_schedule is not None

    requested_schedule_dict = requested_schedule.date_to_dict() if requested_schedule else {}
    personal_schedule_dicts = get_personal_schedule_dicts()

    schedule_request_errors = session.get("schedule_request_errors", None)   
    current_week_num = _week_from_date(_now())

    return render_template(
        SCHEDULE_PERSONAL_TEMPLATE,
        schedule=requested_schedule_dict,
        schedule_request_form=schedule_reqest_form,
        schedule_request_errors=schedule_request_errors,
        personal_schedule_dicts=personal_schedule_dicts,
        current_week_num=current_week_num,
        may_prev=may_prev,
        may_next=may_next
        )


@login_required
@employee_required
@schedule_bp.route("/schedule/calendar", methods=["GET", "POST"])
def calendar():
    calendar_form = CalendarForm()

    if request.method == "POST":
        if calendar_form.validate_on_submit():
            pass
            
    dates = get_calendar_dates(1, 2025)
    first_date = datetime.strptime(dates[0], '%d-%m-%Y')
    first_day_offset = first_date.weekday()
    
    prev_month_days = get_prev_month_days(first_date, first_day_offset)
    next_month_days = get_next_month_days(first_date, first_day_offset + len(dates))

    all_days = prev_month_days + dates + next_month_days
    on_duty_days = get_calendar_on_duty_days(all_days)
    
    week_numbers = get_calendar_week_numbers(dates, first_day_offset)
    week_days = get_shortened_week_days()

    return render_template(
        SCHEDULE_CALENDAR_TEMPLATE,
        calendar_form=calendar_form,
        dates=dates,
        first_day_offset=first_day_offset,
        prev_month_days=prev_month_days,
        next_month_days=next_month_days,
        week_numbers=week_numbers,
        week_days=week_days,
        on_duty_days=on_duty_days
    )


@login_required
@schedule_bp.route("/schedule/verify-employee/<token>", methods=["GET"])
def verify_employee(token):    
    email = confirm_authentication_token(token, EMPLOYEE_VERIFICATION)
    employee_name = session.pop("employee_name", None)
    
    if not employee_name:
        flash(SESSION_ERROR_MSG)
        return redirect(url_for(SCHEDULE_REDIRECT))
    
    if not email:
        flash(AUTHENTICATION_LINK_ERROR_MSG)
        return redirect(url_for(SCHEDULE_REDIRECT))
    
    if not activate_employee(employee_name, email):
        flash(EMPLOYEE_NOT_FOUND_MSG + employee_name)
        return redirect(url_for(SCHEDULE_REDIRECT))
    
    delete_authentication_token(EMPLOYEE_VERIFICATION, token)
    flash(EMPLOYEE_VERIFIED_MSG)
    return redirect(url_for(SCHEDULE_REDIRECT))
