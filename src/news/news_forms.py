from flask_wtf import FlaskForm
from wtforms import TextAreaField, SubmitField
from wtforms.validators import DataRequired

class CommentForm(FlaskForm):
    comment = TextAreaField(
        label="Comment",
        render_kw={"placeholder": "Enter your comment here", "autofocus": False},
        validators=[DataRequired("Comment is required")]
    )
    submit = SubmitField(label="Submit")

