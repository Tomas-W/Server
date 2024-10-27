from pprint import pprint

from flask import render_template, Blueprint, request, redirect, url_for, flash, session
from flask_login import login_required, current_user
from werkzeug.datastructures import MultiDict

from src.models.news_mod import (get_all_news_dict, get_all_unread_dict, get_news_by_id,
                                 get_news_dict_by_id, add_new_comment)
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
            
            news_item = News(
                header="header",
                title="title",
                code=1,
                important="important",
                grid_cols="grid_cols",
                grid_rows="grid_rows",
                info_cols="info_cols",
                info_rows="info_rows",
                author="author",
            )
            server_db_.session.add(news_item)
            server_db_.session.commit()
            
            sanitized_comment = allow_only_styling(comment_form.content.data)
            add_new_comment(id_, sanitized_comment)
            clean_news_session()
            flash("Comment submitted successfully!", "success")
            return redirect(url_for("news.news", id_=id_, _anchor="news-flash"))
        
        session["form_errors"] = comment_form.errors
        session["form_data"] = request.form.to_dict()
        return redirect(url_for("news.news", id_=id_, _anchor="news-flash"))

    form_data = session.pop("form_data", None)
    if form_data:
        comment_form.process(MultiDict(form_data))

    if form_errors is not None:
        comment_form.process(MultiDict(form_data))

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
    all_news_dict = get_all_unread_dict(current_user.id)
    
    return render_template(
        "news/all_news.html",
        page="all_news",
        all_news_dict=all_news_dict,
    )

