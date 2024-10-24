from pprint import pprint

from flask import render_template, Blueprint, request, redirect, url_for, flash, session
from flask_login import login_required, current_user
from werkzeug.datastructures import MultiDict

from src.models.news_mod import get_all_news_dict, get_all_unread_dict, get_news_by_id, get_news_dict_by_id
# from src.news.news_route_utils import get_row_list
from src.news.news_forms import CommentForm


news_bp = Blueprint("news", __name__)


# noinspection PyArgumentList
@news_bp.route("/all-news")
@login_required
def all_news():       
    all_news = get_all_news_dict()


    return render_template(
        "news/all_news.html",
        page="all_news",
        all_news=all_news,
    )


@news_bp.route("/news/<id_>", methods=["GET", "POST"])
@login_required
def news(id_: int):
    news_item = get_news_by_id(id_)
    news_dict = get_news_dict_by_id(id_)
    
    news_item.set_seen_by(current_user.id)
    
    comment_form = CommentForm()
    form_errors = session.pop("form_errors", None)

    if request.method == "POST":
        if comment_form.validate_on_submit():
            flash("Comment submitted successfully!", "success")
            session.pop("form_errors", None)  # Clear previous errors
            session.pop("form_data", None)  # Clear form data on successful submission
            return redirect(url_for("news.news", id_=id_, _anchor="comment-form"))
        
        session["form_errors"] = comment_form.errors  # Store errors if validation fails
        session["form_data"] = request.form.to_dict()  # Store the form data as a dictionary
        return redirect(url_for("news.news", id_=id_, _anchor="comment-form"))  # Redirect to clear POST data

    # Retrieve form data if it exists
    form_data = session.pop("form_data", None)
    if form_data:
        comment_form.process(MultiDict(form_data))  # Convert to MultiDict for repopulation

    # Process form errors if they exist
    if form_errors is not None:
        comment_form.process(MultiDict(form_data))  # Process errors if they exist

    return render_template(
        "news/news.html",
        page="news",
        news_dict=news_dict,
        comment_form=comment_form,
        form_errors=form_errors,
    )


@news_bp.route("/all-unread")
@login_required
def all_unread():
    all_news = get_all_unread_dict(current_user.id)
    
    return render_template(
        "news/all_news.html",
        page="all_news",
        all_news=all_news,
    )

