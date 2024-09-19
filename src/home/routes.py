from flask import render_template, Blueprint
from flask_login import login_required, current_user

home_bp = Blueprint("home", __name__, template_folder='templates')


# noinspection PyArgumentList
@home_bp.route("/home")
@login_required
def home():
    username: str = current_user.username
    return render_template("home.html",
                           page="home",
                           username=username)
