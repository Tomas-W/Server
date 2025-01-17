from flask import (
    abort,
    Blueprint,
    flash,
    redirect,
    render_template, 
    request,
    session,
    url_for,
)
from flask_login import (
    current_user,
    login_required,
)
from werkzeug.datastructures import MultiDict

from src.models.news_model.news_mod_utils import (
    add_new_comment,
    add_news_message,
    delete_comment_by_id,
    delete_news_by_id,
    get_all_news_dict,
    get_all_unread_dict,
    get_comment_by_id,
    get_news_by_id,
    get_news_dict_by_id,
    get_news_id_by_comment_id,
)
from src.models.auth_model.auth_mod_utils import admin_required

from src.routes.news.news_route_utils import (
    allow_only_styling,
    clean_news_session,
)

from src.routes.news.news_forms import AddNewsForm, CommentForm

from src.routes.errors.error_route_utils import Abort404

from config.settings import (
    MESSAGE,
    REDIRECT,
    TEMPLATE,
)

news_bp = Blueprint("news", __name__)


# noinspection PyArgumentList
@news_bp.route("/news/all")
@login_required
def all():
    """Serves all news items with pagination."""
    all_news_dict = get_all_news_dict()
    flash_type = "all_news"

    return render_template(
        TEMPLATE.ALL_NEWS,
        all_news_dict=all_news_dict,
        flash_type=flash_type,
    )


@news_bp.route("/news/unread")
@login_required
def unread():
    all_news_dict = get_all_unread_dict(current_user.id)
    
    return render_template(
        TEMPLATE.ALL_NEWS,
        all_news_dict=all_news_dict,
    )


@news_bp.route("/news/id/<id_>", methods=["GET", "POST"])
@login_required
def news(id_: int):
    """
    Serves news item based on id.
    
    - CommentForm
    """
    news_item = get_news_by_id(id_)
    if not news_item:
        description = f"News item with ID {id_} not found"
        raise Abort404(description=description)
    news_item.set_seen_by(current_user.id)

    news_dict = get_news_dict_by_id(id_)
    comment_form = CommentForm()
    comment_form_errors = session.pop("comment_form_errors", None)
    form_data = session.pop("form_data", None)
    
    if request.method == "POST":
        if comment_form.validate_on_submit():
            sanitized_comment = allow_only_styling(comment_form.content.data)
            add_new_comment(news_id=id_, user_id=current_user.id, content=sanitized_comment)
            clean_news_session()
            flash(MESSAGE.COMMENT_SUCCESS)
            session["post_comment"] = True
            session["flash_type"] = "comment"
            return redirect(url_for(REDIRECT.NEWS, id_=id_, _anchor="comment-flash"))
        
        session["comment_form_errors"] = comment_form.errors
        session["form_data"] = request.form.to_dict()
        return redirect(url_for(REDIRECT.NEWS, id_=id_, _anchor="post-comment-wrapper"))

    if form_data:
        comment_form.process(MultiDict(form_data))

    if comment_form_errors is not None:
        comment_form.process(MultiDict(form_data))
    
    post_comment = session.pop("post_comment", None)  # for comment bg hghlight
    comment_id = session.pop("comment_id", None)      # for like/dislike bg hghlight
    flash_type = session.pop("flash_type", None)      # for flash messages location
    
    return render_template(
        TEMPLATE.NEWS,
        comment_form=comment_form,
        comment_form_errors=comment_form_errors,
        news_dict=news_dict,
        
        post_comment=post_comment,
        comment_id=comment_id,
        flash_type=flash_type,
    )


@news_bp.route("/news/add", methods=["GET", "POST"])
@login_required
@admin_required
def add():
    add_news_form: AddNewsForm = AddNewsForm()
    
    if request.method == "POST":
        if add_news_form.validate_on_submit():
            grid_cols = request.form.getlist("table_cols[]")
            grid_rows = [row.replace("\n", "|") for row in request.form.getlist("table_rows[]")]
            info_cols = request.form.getlist("alinea_headers[]")
            info_rows = request.form.getlist("alinea_contents[]")
            add_news_message(add_news_form,
                             grid_cols,
                             grid_rows,
                             info_cols,
                             info_rows,
                             current_user.id)
            return redirect(url_for(REDIRECT.ALL_NEWS))
        
        session["news_errors"] = add_news_form.errors

    add_news_errors = session.pop("add_news_errors", None)
    
    return render_template(
        TEMPLATE.ADD_NEWS,
        add_news_form=add_news_form,
        add_news_errors=add_news_errors
    )
    

@news_bp.route("/news/delete", defaults={"id_": None}, methods=["GET", "POST"])
@news_bp.route("/news/delete/<id_>", methods=["GET", "POST"])
@login_required
@admin_required
def delete(id_: int):
    if id_:
        news_item = get_news_by_id(id_)
        if not news_item:
            description = f"News item with ID {id_} not found"
            raise Abort404(description=description)
        delete_news_by_id(id_)
        flash(f"News ID {id_} deleted")
        return redirect(url_for(REDIRECT.DELETE_NEWS))
    
    all_news_dict = get_all_news_dict()
    return render_template(
        TEMPLATE.DELETE_NEWS,
        all_news_dict=all_news_dict,
    )


@news_bp.route("/news/like-news/<id_>")
@login_required
def like_news(id_: int):
    news_item = get_news_by_id(id_)
    if not news_item:
        description = f"News item with ID {id_} not found"
        raise Abort404(description=description)
        
    news_item.set_liked_by(current_user.id)
    session["news_id"] = int(id_)
    return redirect(url_for(
        REDIRECT.NEWS,
        id_=id_,
        _anchor="like-dislike"
    ))


@news_bp.route("/news/dislike-news/<id_>")
@login_required
def dislike_news(id_: int):
    news_item = get_news_by_id(id_)
    if not news_item:
        description = f"News item with ID {id_} not found"
        raise Abort404(description=description)
        
    news_item.set_disliked_by(current_user.id)
    session["news_id"] = int(id_)
    return redirect(url_for(
        REDIRECT.NEWS,
        id_=id_,
        _anchor="like-dislike"
    ))


@news_bp.route("/news/delete-comment/<id_>")
@login_required
@admin_required
def delete_comment(id_: int):
    if delete_comment_by_id(id_):
        session["flash_type"] = "delete_comment"
        flash("Comment deleted")
    
    news_id = get_news_id_by_comment_id(id_)
    return redirect(url_for(
        REDIRECT.NEWS,
        id_=news_id,
        _anchor="comment-flash"
    ))


@news_bp.route("/news/like-comment/<id_>")
@login_required
def like_comment(id_: int):
    comment_item = get_comment_by_id(id_)
    if not comment_item:
        description = f"Comment with ID {id_} not found"
        raise Abort404(description=description)
        
    comment_item.set_liked_by(current_user.id)
    session["comment_id"] = int(id_)
    return redirect(url_for(
        REDIRECT.NEWS,
        id_=comment_item.news_id,
        _anchor=f"comment-{id_}"
    ))


@news_bp.route("/news/dislike-comment/<id_>")
@login_required
def dislike_comment(id_: int):
    comment_item = get_comment_by_id(id_)
    if not comment_item:
        description = f"Comment with ID {id_} not found"
        raise Abort404(description=description)
        
    comment_item.set_disliked_by(current_user.id)
    session["comment_id"] = int(id_)
    return redirect(url_for(
        REDIRECT.NEWS,
        id_=comment_item.news_id,
        _anchor=f"comment-{id_}"
    ))


@news_bp.route("/news/profile_icons/<filename>")
@login_required
def profile_icons(filename):
    referrer = request.headers.get("Referer")
    if referrer:
        return redirect(referrer)
    else:
        return redirect(url_for(REDIRECT.ALL_NEWS))  # Fallback if no referrer is available
