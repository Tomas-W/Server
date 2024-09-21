from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, EmailField, PasswordField
from wtforms.fields.simple import BooleanField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo

from config.settings import (banned_username_words, required_password_symbols,
                             banned_username_chars)
from src.admin.form_utils import NewsCheck


class NewsForm(FlaskForm):
    """News form for home page."""
    title = TextAreaField(
        label="Title",
        render_kw={"placeholder": "News title",
                   "autofocus": True},
        validators=[DataRequired(message="Title is required"),
                    Length(min=4, max=75,
                           message="Title must not be 4 - 75 char"),
                    NewsCheck(
                        banned_words=banned_username_words,
                        banned_chars=banned_username_chars,
                        message="Invalid words and or characters"),
                    ])
    content = TextAreaField(
        label="Content",
        render_kw={"placeholder": "Content"},
        validators=[DataRequired(message="Content is required"),
                    Length(min=4, max=1_000_000,
                           message="Content must be 4 - 1_000_000 char"),
                    NewsCheck(
                        banned_words=banned_username_words,
                        banned_chars=banned_username_chars,
                        message="Invalid words and or characters"),
                    ])

    submit = SubmitField(label="Submit")


class RemarkForm(FlaskForm):
    """Remark form for home page."""
    title = TextAreaField(
        label="Title",
        render_kw={"placeholder": "News title",
                   "autofocus": True},
        validators=[DataRequired(message="Title is required"),
                    Length(min=4, max=75,
                           message="Title must not exceed 75 char"),
                    NewsCheck(
                        banned_words=banned_username_words,
                        banned_chars=banned_username_chars,
                        message="Invalid words and or characters"),
                    ])
    content = TextAreaField(
        label="Content",
        render_kw={"placeholder": "Content"},
        validators=[DataRequired(message="Content is required"),
                    Length(min=4, max=1_000_000,
                           message="Length must be 4 - 1_000_000"),
                    NewsCheck(
                        banned_words=banned_username_words,
                        banned_chars=banned_username_chars,
                        message="Invalid words and or characters"),
                    ])

    submit = SubmitField(label="Register")

