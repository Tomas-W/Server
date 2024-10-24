from flask_wtf import FlaskForm
from wtforms import TextAreaField, SubmitField
from wtforms.validators import DataRequired
from src.utils.form_utils import LengthCheck, ForbiddenCheck

class CommentForm(FlaskForm):
    comment = TextAreaField(
        label="Comment",
        render_kw={"placeholder": "Enter your comment here",
                   "autofocus": False},
        validators=[
            DataRequired("Comment is required"),
            LengthCheck(),
            ForbiddenCheck(),            
        ]
    )
    submit = SubmitField(label="Submit")
