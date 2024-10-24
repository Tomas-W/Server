from pprint import pprint

from flask import render_template, Blueprint, request, redirect, url_for, flash, session
from flask_login import login_required, current_user

from src.models.news_mod import get_all_news_dict, get_all_unread_dict, get_news_by_id
from src.news.news_route_utils import get_row_list
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
    row_list = get_row_list(news_item)
    info_list = news_item.info_rows.split("|")
    
    news_item.set_seen_by(current_user.id)
    comment_form = CommentForm()

    form_errors = session.pop("form_errors", None)
    last_form_type = session.pop("last_form_type", None)

    if request.method == "POST":
        if comment_form.validate_on_submit():
            flash("Comment submitted successfully!", "success")
            return redirect(url_for("news.news", id_=id_, _anchor="comment-form"))  # Add _anchor to redirect
        
        else:
            session["form_errors"] = comment_form.errors
            session["last_form_type"] = "comment"
            return redirect(url_for("news.news", id_=id_))

    if form_errors:
        comment_form.comment.errors = form_errors.get("comment", [])

    return render_template(
        "news/news.html",
        page="news",
        news_item=news_item,
        row_list=row_list,
        info_list=info_list,
        comment_form=comment_form,
        form_errors=form_errors or {},
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

