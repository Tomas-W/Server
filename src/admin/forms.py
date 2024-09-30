from flask_wtf import FlaskForm
from wtforms import SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length

from src.auth.form_utils import ForbiddenCheck


class NewsForm(FlaskForm):
    """News form for home page."""
    title = TextAreaField(
        label="Title",
        render_kw={"placeholder": "News title",
                   "autofocus": True},
        validators=[
            DataRequired(message="Title is required"),
            Length(min=4,
                   max=75,
                   message="Title must be 4 - 75 characters"),
            ForbiddenCheck(),
        ]
    )
    content = TextAreaField(
        label="Content",
        render_kw={"placeholder": "Content"},
        validators=[
            DataRequired(message="Content is required"),
            Length(min=4,
                   max=1_000_000,
                   message="Content must be 4 - 1,000,000 characters"),
            ForbiddenCheck(),
        ]
    )
    submit = SubmitField("Submit")


class RemarkForm(FlaskForm):
    """Remark form for home page."""
    title = TextAreaField(
        label="Title",
        render_kw={"placeholder": "Remark title",
                   "autofocus": True},
        validators=[
            DataRequired(message="Title is required"),
            Length(min=4,
                   max=75,
                   message="Title must be 4 - 75 characters"),
            ForbiddenCheck(),
        ]
    )
    content = TextAreaField(
        label="Content",
        render_kw={"placeholder": "Content"},
        validators=[
            DataRequired(message="Content is required"),
            Length(min=4,
                   max=1_000_000,
                   message="Content must be 4 - 1,000,000 characters"),
            ForbiddenCheck(),
        ]
    )
    submit = SubmitField("Submit")

