import calendar

from datetime import (
    datetime,
    timedelta,
    date,
)
from flask import request
from flask_login import current_user

from src.extensions import logger


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


def get_personal_hours_per_week(schedule: dict) -> int:
    total_hours = []
    for week in schedule:
        week_hours = 0
        for day in week:
            total_quarters = 0
            if day["end"]:
                work_quarters = (int(day["end"]) - int(day["start"]))
                break_quarters = int(day["break_time"].split(":")[0]) * 4
                break_quarters += int(day["break_time"].split(":")[1]) / 15
                total_quarters += work_quarters - break_quarters
                week_hours += total_quarters / 4
        total_hours.append(week_hours)
    return total_hours


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


def get_calendar_dates(month: int, year: int) -> list[date]:
    """
    Returns a list of dates in the format 'dd-mm-yyyy' the in the given month and year.
    """
    _, num_days = calendar.monthrange(year, month)
    return [
        date(year, month, day).strftime('%d-%m-%Y') 
        for day in range(1, num_days + 1)
    ]


def get_prev_month_days(first_date: datetime, first_day_offset: int) -> list:
    """Calculate the days needed from the previous month to fill the calendar."""
    prev_month_days = []
    if first_day_offset > 0:
        last_month = first_date.replace(day=1) - timedelta(days=1)
        for i in range(first_day_offset):
            day = last_month - timedelta(days=i)
            prev_month_days.insert(0, day.strftime('%d-%m-%Y'))
    return prev_month_days


def get_next_month_days(first_date: datetime, total_days: int) -> list:
    """Calculate the days needed from the next month to fill the calendar."""
    next_month_days = []
    if total_days >= 35:
        target_days = 42  # Fill to 6 weeks
    else:
        target_days = 35  # Fill to 5 weeks
        
    if total_days < target_days:
        next_month = (first_date.replace(day=28) + timedelta(days=4)).replace(day=1)
        days_needed = target_days - total_days
        for i in range(days_needed):
            day = next_month + timedelta(days=i)
            next_month_days.append(day.strftime('%d-%m-%Y'))
    return next_month_days


def get_calendar_week_numbers(dates: list[str], first_day_offset: int) -> list[int]:
    """Get week numbers for each row of the calendar."""
    # Get the first Sunday (or first day) of the calendar view
    first_date = datetime.strptime(dates[0], '%d-%m-%Y')
    calendar_start = first_date - timedelta(days=first_day_offset)
    
    # Get week number for each week (each 7-day interval)
    week_numbers = []
    for i in range(0, 42, 7):  # Max 6 weeks
        week_date = calendar_start + timedelta(days=i)
        week_numbers.append(week_date.isocalendar()[1])
        if i >= 28 and i//7 >= (len(dates) + first_day_offset - 1)//7:
            break
            
    return week_numbers


def get_shortened_week_days() -> list[str]:
    """
    Returns the string representation of the days of the week.
    """
    day_names = [calendar.day_name[day][:3] for day in range(7)]
    return day_names
