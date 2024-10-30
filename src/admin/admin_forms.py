from flask_wtf import FlaskForm
from wtforms import (SubmitField, TextAreaField, HiddenField, EmailField, StringField, 
                     PasswordField)
from wtforms.validators import DataRequired, EqualTo

from src.utils.form_utils import (ForbiddenCheck, UsernameTakenCheck, PasswordCheck,
                                  EmailTakenCheck, UsernameLengthCheck, PasswordLengthCheck,
                                  EmailCheck, EmailLengthCheck, FastNameLengthCheck,
                                  FastCodeCheck, FastCodeLengthCheck, VerifyEmailCheck,
                                  NewsTitleLengthCheck, NewsContentLengthCheck,
                                  CommentTitleLengthCheck, CommentLengthCheck)


class VerifyEmailForm(FlaskForm):
    """
    User admin-page Verify Email Form.
    
    Fields:
    - email
    """
    #  Placeholder is overwritten in html by current_user's data
    #  If field is empty, current user's email is used.
    email = EmailField(
        label="Email",
        render_kw={"placeholder": "Example@example.com", "autofocus": True},
        validators=[
            VerifyEmailCheck(),
        ]
    )
    form_type = HiddenField(default="verify")
    submit = SubmitField(label="Verify")


class AuthenticationForm(FlaskForm):
    """
    User admin-page Authentication Form.
    Validated individually to allow individual db updates.
    
    Fields:
    - email
    - username
    - password
    - confirm_password
    - fast_name
    - fast_code
    """
    #  Username, email and fast name placeholders
    # are overwritten in html by current_user's data
    email = EmailField(
        label="email",
        render_kw={"placeholder": "example@example.com"},
        validators=[
            EmailCheck(admin=True),
            EmailTakenCheck(admin=True),
            EmailLengthCheck(admin=True),
        ]
    )
    username = StringField(
        label="username",
        render_kw={"placeholder": "username"},
        validators=[
            ForbiddenCheck(),
            UsernameTakenCheck(admin=True),
            UsernameLengthCheck(admin=True),
        ]
    )
    password = PasswordField(
        label="password",
        render_kw={},
        validators=[
            PasswordCheck(admin=True),
            PasswordLengthCheck(admin=True),
            EqualTo(fieldname="confirm_password", message="Passwords must match"),
        ]
    )
    confirm_password = PasswordField(
        label="confirm password",
        render_kw={},
        validators=[
            PasswordCheck(admin=True),
            PasswordLengthCheck(admin=True),
            EqualTo(fieldname="password", message="Passwords must match"),
        ]
    )
    fast_name = StringField(
        label="fast name",
        render_kw={"placeholder": "fast name"},
        validators=[
            ForbiddenCheck(),
            FastNameLengthCheck(admin=True),
        ]
    )
    fast_code = PasswordField(
        label="fast code",
        render_kw={"inputmode": "numeric"},
        validators=[
            FastCodeCheck(admin=True),
            FastCodeLengthCheck(admin=True),
        ]
    )
    form_type = HiddenField(default="authentication")
    submit = SubmitField(label="Update")


class NewsForm(FlaskForm):
    """
    Master admin-page News Form.
    All fields are required.
    
    Fields:
    - title
    - content
    """
    title = TextAreaField(
        label="Title",
        render_kw={"placeholder": "News title"},
        validators=[
            DataRequired(message="Title is required"),
            NewsTitleLengthCheck(),
            ForbiddenCheck(),
        ]
    )
    content = TextAreaField(
        label="Content",
        render_kw={"placeholder": "Content"},
        validators=[
            DataRequired(message="Content is required"),
            NewsContentLengthCheck(),
            ForbiddenCheck(),
        ]
    )
    form_type = HiddenField(default="news")
    submit = SubmitField("Submit")


class CommentForm(FlaskForm):
    """
    Master admin-page Comment Form.
    Title field is optional.
    
    Fields:
    - title
    - content
    """
    title = TextAreaField(
        label="Title",
        render_kw={"placeholder": "Comment title"},
        validators=[
            CommentTitleLengthCheck(),
            ForbiddenCheck(),
        ]
    )
    content = TextAreaField(
        label="Content",
        render_kw={"placeholder": "Content"},
        validators=[
            DataRequired(message="Comment is required"),
            CommentLengthCheck(),
            ForbiddenCheck(),
        ]
    )
    form_type = HiddenField(default="comment")
    submit = SubmitField("Submit")
    