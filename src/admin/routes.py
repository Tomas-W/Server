from flask import render_template, Blueprint, url_for, redirect
from flask_login import login_required

from src.admin.forms import NewsForm
from src.admin.route_utils import add_news_message

admin_bp = Blueprint("admin", __name__)


@admin_bp.route("/add-news", methods=["GET", "POST"])
@login_required
def add_news():
    news_form: NewsForm = NewsForm()
    if news_form.validate_on_submit():
        add_news_message(news_form.title.data,
                         news_form.content.data)
        return redirect(url_for("home.home"))

    return render_template(
        "admin/add_news.html",
        page="add_news",
        news_form=news_form,
    )
