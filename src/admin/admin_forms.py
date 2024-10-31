from flask_wtf import FlaskForm
from wtforms import (SubmitField, TextAreaField, HiddenField, EmailField, StringField, 
                     PasswordField)
from wtforms.validators import DataRequired, EqualTo

from src.utils.form_utils import (ForbiddenCheck, UsernameTakenCheck, PasswordCheck,
                                  EmailTakenCheck, UsernameLengthCheck, PasswordLengthCheck,
                                  EmailCheck, EmailLengthCheck, FastNameLengthCheck,
                                  FastCodeCheck, FastCodeLengthCheck, VerifyEmailCheck,
                                  NewsTitleLengthCheck, NewsContentLengthCheck,
                                  CommentLengthCheck)
from config.settings import (PWD_MATCH_MSG, REQUIRED_FIELD_MSG)

class VerifyEmailForm(FlaskForm):
    """
    Used on user_admin-page to verify email.
    All fields are required and validated.
    Placeholder may be overwritten in html by current_user's email.

    Fields:
    - email [EmailField] [Required]
    - form_type [HiddenField]
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
    form_type = HiddenField(default="verify_form")
    submit = SubmitField(label="Verify")


class AuthenticationForm(FlaskForm):
    """
    Used on user_admin-page to update user's data.
    Allows empty fields for individual updates.
    Username, email and fast name placeholders
     may be overwritten in html by current_user's data.
    
    Fields:
    - email [EmailField] [Optional]
    - username [StringField] [Optional]
    - password [PasswordField] [Optional]
    - confirm_password [PasswordField] [Optional]
    - fast_name [StringField] [Optional]
    - fast_code [PasswordField] [Optional]
    - form_type [HiddenField]
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
            EqualTo(fieldname="confirm_password", message=PWD_MATCH_MSG),
        ]
    )
    confirm_password = PasswordField(
        label="confirm password",
        render_kw={},
        validators=[
            PasswordCheck(admin=True),
            PasswordLengthCheck(admin=True),
            EqualTo(fieldname="password", message=PWD_MATCH_MSG),
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
    form_type = HiddenField(default="authentication_form")
    submit = SubmitField(label="Update")


class NewsForm(FlaskForm):
    """
    Used on news_admin-page to add news.
    
    Fields:
    - title [TextAreaField] [Required]
    - content [TextAreaField] [Required]
    - form_type [HiddenField]
    """
    title = TextAreaField(
        label="Title",
        render_kw={"placeholder": "News title"},
        validators=[
            DataRequired(message=REQUIRED_FIELD_MSG),
            NewsTitleLengthCheck(),
            ForbiddenCheck(),
        ]
    )
    content = TextAreaField(
        label="Content",
        render_kw={"placeholder": "Content"},
        validators=[
            DataRequired(message=REQUIRED_FIELD_MSG),
            NewsContentLengthCheck(),
            ForbiddenCheck(),
        ]
    )
    form_type = HiddenField(default="news_form")
    submit = SubmitField("Submit")


class CommentForm(FlaskForm):
    """
    Used on comment_admin-page to add comment.
    All fields are required and validated.
    
    Fields:
    - content [TextAreaField] [Required]
    - form_type [HiddenField]
    """
    content = TextAreaField(
        label="Content",
        render_kw={"placeholder": "Content"},
        validators=[
            DataRequired(message=REQUIRED_FIELD_MSG),
            CommentLengthCheck(),
            ForbiddenCheck(),
        ]
    )
    form_type = HiddenField(default="comment_form")
    submit = SubmitField("Submit")
    