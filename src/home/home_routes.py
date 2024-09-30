from flask import render_template, Blueprint
from flask_login import login_required, current_user

from src.home.home_route_utils import get_all_news

home_bp = Blueprint("home", __name__)


# noinspection PyArgumentList
@home_bp.route("/home")
@login_required
def home():
    try:
        username: str = current_user.username
    except AttributeError:
        username = "NoLogin"
    all_news = get_all_news()

    return render_template(
        "home.html",
        page="home",
        username=username,
        all_news=all_news,
    )
