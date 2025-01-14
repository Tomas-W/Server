from flask_wtf import FlaskForm
from wtforms import (
    BooleanField,
    EmailField,
    HiddenField,
    PasswordField,
    StringField,
    SubmitField,
)
from wtforms.validators import (
    DataRequired,
    Email,
    EqualTo,
)

from src.utils.form_utils import (
    EmailCheck,
    EmailLengthCheck,
    EmailTakenCheck,
    ForbiddenCheck,
    PasswordCheck,
    PasswordLengthCheck,
    UsernameLengthCheck,
    UsernameTakenCheck,
)

from config.settings import (
    FORM,
    MESSAGE,
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
            EqualTo(fieldname="password", message=MESSAGE.PWD_MATCH),
            PasswordCheck(),
            PasswordLengthCheck(),
        ]
    )
    form_type = HiddenField(default=FORM.REGISTER)
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
            DataRequired(message=MESSAGE.REQUIRED_FIELD),
        ]
    )
    password = PasswordField(
        label="Password",
        render_kw={"placeholder": "Password"},
        validators=[
            DataRequired(message=MESSAGE.REQUIRED_FIELD),
        ]
    )
    remember = BooleanField("Remember me")
    form_type = HiddenField(default=FORM.LOGIN)
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
            DataRequired(message=MESSAGE.REQUIRED_FIELD),
        ]
    )
    fast_code = PasswordField(
        label="Login",
        render_kw={
            "placeholder": "Login",
            "inputmode": "numeric",
        },
        validators=[
            DataRequired(message=MESSAGE.REQUIRED_FIELD),
        ]
    )
    form_type = HiddenField(default=FORM.FAST_LOGIN)
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
            DataRequired(message=MESSAGE.REQUIRED_FIELD),
            Email(message=MESSAGE.INVALID_EMAIL),
            EmailLengthCheck(),
        ]
    )
    form_type = HiddenField(default=FORM.REQUEST_RESET)
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
            DataRequired(message=MESSAGE.REQUIRED_FIELD),
            PasswordCheck(),
            PasswordLengthCheck(),
        ]
    )
    confirm_password = PasswordField(
        label="Confirm password",
        render_kw={"placeholder": "Confirm password"},
        validators=[
            DataRequired(message=MESSAGE.REQUIRED_FIELD),
            EqualTo(fieldname="password"),
            PasswordCheck(),
            PasswordLengthCheck(),
        ]
    )
    form_type = HiddenField(default=FORM.SET_PASSWORD)
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
            DataRequired(message=MESSAGE.REQUIRED_FIELD),
            PasswordCheck(),
            PasswordLengthCheck(),
        ]
    )
    confirm_password = PasswordField(
        label="Confirm password",
        render_kw={"placeholder": "Confirm password"},
        validators=[
            DataRequired(message=MESSAGE.REQUIRED_FIELD),
            EqualTo(fieldname="password", message=MESSAGE.PWD_MATCH),
            PasswordCheck(),
            PasswordLengthCheck(),
        ]
    )
    form_type = HiddenField(default=FORM.RESET_PASSWORD)
    submit = SubmitField(label="Reset")
