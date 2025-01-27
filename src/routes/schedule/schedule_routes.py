from datetime import (
    datetime,
    timedelta,
)
from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from flask_login import current_user, login_required

from src.extensions import logger

from src.models.schedule_model.schedule_mod import Schedule
from src.models.schedule_model.schedule_mod_utils import (
    activate_employee,
    get_calendar_on_duty_days,
)
from src.models.auth_model.auth_mod_utils import (
    confirm_authentication_token,
    delete_authentication_token,
    employee_required,
)
from src.models.schedule_model.schedule_mod_utils import get_schedule_bounds

from src.routes.schedule.schedule_route_utils import (
    get_calendar_dates,
    get_calendar_week_numbers,
    get_next_month_days,
    get_personal_hours_per_week,
    get_personal_schedule_dicts,
    get_prev_month_days,
    get_requested_date,
    get_shortened_week_days,
)

from src.routes.schedule.schedule_forms import (
    CalendarForm,
)

from src.utils.schedule import _now, _week_from_date

from config.settings import (
    MESSAGE,
    REDIRECT,
    SERVER,
    TEMPLATE,
)

schedule_bp = Blueprint("schedule", __name__)


@schedule_bp.route("/schedule/personal", methods=["GET"])
@schedule_bp.route("/schedule/<date>", methods=["GET"])
@employee_required
@login_required
def personal(date: str = None):
    requested_date = get_requested_date(date)

    earliest_schedule, latest_schedule = get_schedule_bounds()
    may_prev = earliest_schedule and requested_date > earliest_schedule.date
    may_next = latest_schedule and requested_date < latest_schedule.date

    requested_schedule = Schedule.query.filter_by(date=requested_date).one_or_none()
    requested_schedule_dict = requested_schedule.date_to_dict() if requested_schedule else {}
    personal_schedule_dicts = get_personal_schedule_dicts()
    personal_hours_per_week = get_personal_hours_per_week(personal_schedule_dicts)

    current_week_num = _week_from_date(_now())

    logger.info(f"{requested_date=}")
    logger.info(f"{earliest_schedule.date=}")
    logger.info(f"{latest_schedule.date=}")

    return render_template(
        TEMPLATE.PERSONAL,
        schedule=requested_schedule_dict,
        personal_schedule_dicts=personal_schedule_dicts,
        personal_hours_per_week=personal_hours_per_week,
        current_week_num=current_week_num,
        may_prev=may_prev,
        may_next=may_next
        )


@schedule_bp.route("/schedule/calendar", methods=["GET", "POST"])
@employee_required
@login_required
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
        TEMPLATE.CALENDAR,
        calendar_form=calendar_form,
        dates=dates,
        first_day_offset=first_day_offset,
        prev_month_days=prev_month_days,
        next_month_days=next_month_days,
        week_numbers=week_numbers,
        week_days=week_days,
        on_duty_days=on_duty_days
    )
