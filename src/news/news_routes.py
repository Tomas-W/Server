from pprint import pprint

from flask import render_template, Blueprint, request, redirect, url_for, flash, session
from flask_login import login_required, current_user
from werkzeug.datastructures import MultiDict

from src.models.news_mod import (get_all_news_dict, get_all_unread_dict, get_news_by_id,
                                 get_news_dict_by_id, get_comment_by_id, add_new_comment)
from src.news.news_forms import CommentForm
from src.news.news_route_utils import allow_only_styling, clean_news_session
from src.models.news_mod import News
from src.extensions import server_db_
news_bp = Blueprint("news", __name__)


# noinspection PyArgumentList
@news_bp.route("/all-news")
@login_required
def all_news():       
    all_news_dict = get_all_news_dict()

    return render_template(
        "news/all_news.html",
        page="all_news",
        all_news_dict=all_news_dict,
    )


@news_bp.route("/news/<id_>", methods=["GET", "POST"])
@login_required
def news(id_: int):
    news_dict = get_news_dict_by_id(id_)
    news_item = get_news_by_id(id_)
    news_item.set_seen_by(current_user.id)
    
    comment_form = CommentForm()
    form_errors = session.pop("form_errors", None)

    if request.method == "POST":
        if comment_form.validate_on_submit():
            sanitized_comment = allow_only_styling(comment_form.content.data)
            add_new_comment(id_, sanitized_comment)
            clean_news_session()
            flash("Comment submitted successfully!", "success")
            session["post_comment"] = True
            return redirect(url_for("news.news", id_=id_, _anchor="comment-flash"))
        
        session["form_errors"] = comment_form.errors
        session["form_data"] = request.form.to_dict()
        return redirect(url_for("news.news", id_=id_, _anchor="comment-container"))

    form_data = session.pop("form_data", None)
    if form_data:
        comment_form.process(MultiDict(form_data))

    if form_errors is not None:
        comment_form.process(MultiDict(form_data))
    
    news_id = session.pop("news_id", None)
    post_comment = session.pop("post_comment", None)
    comment_id = session.pop("comment_id", None)
    return render_template(
        "news/news.html",
        page="news",
        news_dict=news_dict,
        comment_form=comment_form,
        form_errors=form_errors,
        user_id=str(current_user.id),
        news_id=news_id,
        post_comment=post_comment,
        comment_id=comment_id,
    )
    

@news_bp.route("/like-news/<id_>")
@login_required
def like_news(id_: int):
    news_item = get_news_by_id(id_)
    news_item.set_liked_by(current_user.id)
    session["news_id"] = int(id_)
    return redirect(url_for("news.news", id_=id_, _anchor="like-dislike"))


@news_bp.route("/dislike-news/<id_>")
@login_required
def dislike_news(id_: int):
    news_item = get_news_by_id(id_)
    news_item.set_disliked_by(current_user.id)
    session["news_id"] = int(id_)
    return redirect(url_for("news.news", id_=id_, _anchor="like-dislike"))


@news_bp.route("/like-comment/<id_>")
@login_required
def like_comment(id_: int):
    comment_item = get_comment_by_id(id_)
    comment_item.set_liked_by(current_user.id)
    session["comment_id"] = int(id_)
    return redirect(url_for("news.news", id_=comment_item.news_id, _anchor=f"comment-{id_}"))


@news_bp.route("/dislike-comment/<id_>")
@login_required
def dislike_comment(id_: int):
    comment_item = get_comment_by_id(id_)
    comment_item.set_disliked_by(current_user.id)
    session["comment_id"] = int(id_)
    return redirect(url_for("news.news", id_=comment_item.news_id, _anchor=f"comment-{id_}"))


@news_bp.route("/all-unread")
@login_required
def all_unread():
    all_news_dict = get_all_unread_dict(current_user.id)
    
    return render_template(
        "news/all_news.html",
        page="all_news",
        all_news_dict=all_news_dict,
    )

