from flask import Blueprint, render_template, request
from datetime import datetime, timedelta
from src.models.schedule_model.schedule_mod import Schedule
from config.settings import SCHEDULE_TEMPLATE
from src.extensions import logger
from src.routes.schedule.schedule_route_utils import test_update_schedule
schedule_bp = Blueprint("schedule", __name__)


@schedule_bp.route("/schedule/today", methods=["GET"])
@schedule_bp.route("/schedule/<date>", methods=["GET"])
def today(date: str = None):
    sub = request.args.get("sub", "False") == "True"
    add = request.args.get("add", "False") == "True"
    
    if not date:
        today_date = datetime.now().date()
    else:
        today_date = datetime.strptime(date, "%Y-%m-%d").date()
        
    if sub:
        today_date -= timedelta(days=1)
    elif add:
        today_date += timedelta(days=1)
        
    today_schedule = Schedule.query.filter_by(date=today_date).first()

    today_schedule_dict = today_schedule.date_to_dict() if today_schedule else {}
    
    test_update_schedule()
    
    return render_template(
        SCHEDULE_TEMPLATE,
        display_table=True,
        schedule=today_schedule_dict
        )
