import json
from datetime import datetime, timedelta
from src.models.schedule_model.schedule_mod import Schedule
from src.routes.schedule.schedule_route_utils import get_week_days
from src.extensions import server_db_, logger
from config.settings import SCHEDULE_PATH


def get_date_from_week_number(week_number: int, day: str) -> datetime:
    first_day_of_year = datetime(datetime.now().year, 1, 1)
    week_days = get_week_days()
    days_to_add = (week_number - 1) * 7 + week_days.index(day)
    return first_day_of_year + timedelta(days=days_to_add)


def _init_schedule() -> None:
    with open(SCHEDULE_PATH, "r") as json_file:
        schedule_data = json.load(json_file)
    
    for week_number, week_data in schedule_data.items():
        for day, day_data in week_data.items():
            names = day_data["names"]
            hours = [hour.split("|")[0] for hour in day_data["hours"]]
            date = get_date_from_week_number(int(week_number), day).date()
            
            schedule_item = Schedule(date=date,
                                     week_number=week_number,
                                     day=day,
                                     names=names,
                                     hours=hours)
            server_db_.session.add(schedule_item)
    server_db_.session.commit()
    
    
