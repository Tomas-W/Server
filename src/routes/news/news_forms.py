from flask_wtf import FlaskForm
from wtforms import (
    HiddenField,
    SubmitField,
    TextAreaField,
)
from wtforms.validators import DataRequired

from src.utils.form_utils import (
    CommentLengthCheck,
    ForbiddenCheck,
    NewsHeaderLengthCheck,
    NewsTitleLengthCheck,
    NewsCodeCheck,
    NewsImportantLengthCheck,
)


class AddNewsForm(FlaskForm):
    """
    Used on admin.news.add-news page to add news.
    
    Fields:
    - TITLE [TextAreaField] [Required]
    - CONTENT [TextAreaField] [Required]
    - FORM_TYPE [HiddenField]
    """
    header = TextAreaField(
        label="Header",
        render_kw={},
        validators=[
            NewsHeaderLengthCheck(),
            ForbiddenCheck(admin=True),
        ]
    )
    title = TextAreaField(
        label="Title",
        render_kw={},
        validators=[
            NewsTitleLengthCheck(),
            ForbiddenCheck(admin=True),
        ]
    )
    code = TextAreaField(
        label="Code",
        render_kw={},
        validators=[
            NewsCodeCheck(),
        ]
    )
    important = TextAreaField(
        label="Important",
        render_kw={},
        validators=[
            NewsImportantLengthCheck(),
            ForbiddenCheck(admin=True),
        ]
    )

    author = TextAreaField(
        label="Author",
        render_kw={},
        validators=[
            DataRequired(),
            ForbiddenCheck(admin=True),
        ]
    )
    form_type = HiddenField(default="news_form")
    submit = SubmitField("Submit")


class CommentForm(FlaskForm):
    """
    Used on news-page to submit a comment.
    All fields are required and validated.
    
    Fields:
    - content [TextAreaField] [Required]
    - form_type [HiddenField]
    """
    content = TextAreaField(
        label="Comment",
        render_kw={"placeholder": "Enter your comment here"},
        validators=[
            CommentLengthCheck(),
            ForbiddenCheck(),            
        ]
    )
    form_type = HiddenField(default="comment")
    submit = SubmitField(label="Submit")
