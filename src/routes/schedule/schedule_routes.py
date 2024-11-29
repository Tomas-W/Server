from flask import Blueprint, render_template

from config.settings import SCHEDULE_TEMPLATE


schedule_bp = Blueprint("schedule", __name__)


@schedule_bp.route("/schedule/today", methods=["GET"])
def today():
    
    schedule = [
        ("Andreas C", 0, 6*4 - 1, "06:00", "12:00"),
        ("Tomas W", 0, 7*4 - 1, "06:00", "13:00"),
        ("Bart de B", 4, 9*4 - 1, "07:00", "15:00"),
        ("Nataliya van de R", 7*4, 16*4 - 1, "13:00", "20:15"),
        ("Tomas W", 7*4, 16*4 - 1, "13:00", "20:15"),
    ]
    
    return render_template(
        SCHEDULE_TEMPLATE,
        display_table=True,
        schedule=schedule
        )
