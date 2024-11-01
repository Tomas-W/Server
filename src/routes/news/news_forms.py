from flask_wtf import FlaskForm
from wtforms import TextAreaField, SubmitField, HiddenField
from wtforms.validators import DataRequired

from src.utils.form_utils import CommentLengthCheck, ForbiddenCheck
from config.settings import REQUIRED_FIELD_MSG


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
        render_kw={"placeholder": "Enter your comment here",
                   "autofocus": False},
        validators=[
            DataRequired(REQUIRED_FIELD_MSG),
            CommentLengthCheck(),
            ForbiddenCheck(),            
        ]
    )
    form_type = HiddenField(default="comment")
    submit = SubmitField(label="Submit")
