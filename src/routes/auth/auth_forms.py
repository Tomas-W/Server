from flask_wtf import FlaskForm
from wtforms import (
    StringField, SubmitField, EmailField, PasswordField, BooleanField, HiddenField
)
from wtforms.validators import DataRequired, Email, EqualTo

from src.utils.form_utils import (
    EmailCheck, EmailTakenCheck, PasswordCheck, ForbiddenCheck, UsernameTakenCheck,
    EmailLengthCheck, UsernameLengthCheck, PasswordLengthCheck
)
from config.settings import (
    REQUIRED_FIELD_MSG, PWD_MATCH_MSG, INVALID_EMAIL_MSG,
    REGISTER_FORM_TYPE, LOGIN_FORM_TYPE, FAST_LOGIN_FORM_TYPE,
    REQUEST_RESET_FORM_TYPE, SET_PASSWORD_FORM_TYPE, RESET_PASSWORD_FORM_TYPE
)


class RegisterForm(FlaskForm):
    """
    Used on auth.register page to register a new user.
    All fields are required and validated.
    
    Fields:
    - EMAIL [EmailField] [Required]
    - USERNAME [StringField] [Required]
    - PASSWORD [PasswordField] [Required]
    - CONFIRM_PASSWORD [PasswordField] [Required]
    - FORM_TYPE [HiddenField]
    """
    email = EmailField(
        label="Email",
        render_kw={"placeholder": "Email"},
        validators=[
            EmailCheck(),
            EmailTakenCheck(),
            EmailLengthCheck(),
            ForbiddenCheck(),
        ]
    )
    username = StringField(
        label="Username",
        render_kw={"placeholder": "Username"},
        validators=[
            UsernameTakenCheck(),
            UsernameLengthCheck(),
            ForbiddenCheck(),
        ]
    )
    password = PasswordField(
        label="Password",
        render_kw={"placeholder": "Password"},
        validators=[
            PasswordCheck(),
            PasswordLengthCheck(),
        ]
    )
    confirm_password = PasswordField(
        label="Confirm password",
        render_kw={"placeholder": "Confirm password"},
        validators=[
            EqualTo(fieldname="password", message=PWD_MATCH_MSG),
            PasswordCheck(),
            PasswordLengthCheck(),
        ]
    )
    form_type = HiddenField(default=REGISTER_FORM_TYPE)
    submit = SubmitField(label="Register")


class LoginForm(FlaskForm):
    """
    Used on auth.login page to login a user.
    Remember me for cookies.
    
    Fields:
    - EMAIL_OR_UNAME [EmailField] [Required]
    - PASSWORD [PasswordField] [Required]
    - REMEMBER [BooleanField] [Optional]
    - FORM_TYPE [HiddenField]
    """
    email_or_uname = EmailField(
        label="Email or username",
        render_kw={"placeholder": "Email or username"},
        validators=[
            DataRequired(message=REQUIRED_FIELD_MSG),
        ]
    )
    password = PasswordField(
        label="Password",
        render_kw={"placeholder": "Password"},
        validators=[
            DataRequired(message=REQUIRED_FIELD_MSG),
        ]
    )
    remember = BooleanField("Remember me")
    form_type = HiddenField(default=LOGIN_FORM_TYPE)
    submit = SubmitField(label="Login")


class FastLoginForm(FlaskForm):
    """
    Used on all auth pages to login a user via fast name and fast code.
    All fields are required and validated.
    
    Fields:
    - FAST_NAME [StringField] [Required]
    - FAST_CODE [PasswordField] [Required]
    - FORM_TYPE [HiddenField]
    """
    fast_name = StringField(
        label="Name",
        render_kw={"placeholder": "Fast"},
        validators=[
            DataRequired(message=REQUIRED_FIELD_MSG),
        ]
    )
    fast_code = PasswordField(
        label="Login",
        render_kw={
            "placeholder": "Login",
            "inputmode": "numeric",
        },
        validators=[
            DataRequired(message=REQUIRED_FIELD_MSG),
        ]
    )
    form_type = HiddenField(default=FAST_LOGIN_FORM_TYPE)
    submit = SubmitField(label="Go")


class RequestResetForm(FlaskForm):
    """
    Used on auth.request-reset page to request a reset password email.
    All fields are required and validated.
    
    Fields:
    - EMAIL [EmailField] [Required]
    - FORM_TYPE [HiddenField]
    """
    email = EmailField(
        label="Email",
        render_kw={"placeholder": "Example@example.com"},
        validators=[
            DataRequired(message=REQUIRED_FIELD_MSG),
            Email(message=INVALID_EMAIL_MSG),
            EmailLengthCheck(),
        ]
    )
    form_type = HiddenField(default=REQUEST_RESET_FORM_TYPE)
    submit = SubmitField(label="Request")


class SetPasswordForm(FlaskForm):
    """
    Used on auth.set-password page to set a new password.
    All fields are required and validated.
    
    Fields:
    - PASSWORD [PasswordField] [Required]
    - CONFIRM_PASSWORD [PasswordField] [Required]
    - FORM_TYPE [HiddenField]
    """
    password = PasswordField(
        label="Password",
        render_kw={"placeholder": "Password"},
        validators=[
            DataRequired(message=REQUIRED_FIELD_MSG),
            PasswordCheck(),
            PasswordLengthCheck(),
        ]
    )
    confirm_password = PasswordField(
        label="Confirm password",
        render_kw={"placeholder": "Confirm password"},
        validators=[
            DataRequired(message=REQUIRED_FIELD_MSG),
            EqualTo(fieldname="password"),
            PasswordCheck(),
            PasswordLengthCheck(),
        ]
    )
    form_type = HiddenField(default=SET_PASSWORD_FORM_TYPE)
    submit = SubmitField(label="Set")


class ResetPasswordForm(FlaskForm):
    """
    Used on auth.reset-password page to reset password.
    All fields are required and validated.
    
    Fields:
    - PASSWORD [PasswordField] [Required]
    - CONFIRM_PASSWORD [PasswordField] [Required]
    - FORM_TYPE [HiddenField]
    """
    password = PasswordField(
        label="Password",
        render_kw={"placeholder": "Password"},
        validators=[
            DataRequired(message=REQUIRED_FIELD_MSG),
            PasswordCheck(),
            PasswordLengthCheck(),
        ]
    )
    confirm_password = PasswordField(
        label="Confirm password",
        render_kw={"placeholder": "Confirm password"},
        validators=[
            DataRequired(message=REQUIRED_FIELD_MSG),
            EqualTo(fieldname="password", message=PWD_MATCH_MSG),
            PasswordCheck(),
            PasswordLengthCheck(),
        ]
    )
    form_type = HiddenField(default=RESET_PASSWORD_FORM_TYPE)
    submit = SubmitField(label="Reset")
