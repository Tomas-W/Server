from flask_wtf import FlaskForm
from wtforms import TextAreaField, SubmitField
from wtforms.validators import DataRequired

from src.utils.form_utils import CommentLengthCheck, ForbiddenCheck


class CommentForm(FlaskForm):
    content = TextAreaField(
        label="Comment",
        render_kw={"placeholder": "Enter your comment here",
                   "autofocus": False},
        validators=[
            DataRequired("Comment is required"),
            CommentLengthCheck(),
            ForbiddenCheck(),            
        ]
    )
    submit = SubmitField(label="Submit")
