from datetime import datetime, timedelta
from flask import request
from flask_login import current_user


def get_personal_schedule_dicts() -> list[list[dict]]:
    """
    Returns the personal schedule for the latest 5 weeks.
    """
    from src.models.schedule_model.schedule_mod import Schedule
    latest_schedules = (
        Schedule.query
        .order_by(Schedule.date.desc())
        .limit(5*7)
        .all()
    )
    schedules = []
    for i in range(0, len(latest_schedules), 7):
        week = latest_schedules[i:i+7]
        week_dicts = [schedule.to_personal_dict(current_user.employee_name) for schedule in week][::-1]
        schedules.append(week_dicts)
    
    return schedules


def personal_dicts_to_calendar_dicts(personal_dicts: list[dict]) -> list[dict]:
    pass


def get_requested_date(date: str | None = None) -> datetime.date:
    """
    Returns the date requested by the user by 
     adding or subtracting 1 day from the previous date.
    """
    sub = request.args.get("sub", "False") == "True"
    add = request.args.get("add", "False") == "True"
    
    if not date:
        today_date = datetime.now().date()
    else:
        today_date = datetime.strptime(date, "%d-%m-%Y").date()
        
    if sub:
        today_date -= timedelta(days=1)
    elif add:
        today_date += timedelta(days=1)

    return today_date
