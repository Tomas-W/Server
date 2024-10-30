from flask_wtf import FlaskForm
from wtforms import (StringField, SubmitField, EmailField, PasswordField, BooleanField,
                     HiddenField)
from wtforms.validators import DataRequired, Email, EqualTo

from src.utils.form_utils import (EmailTakenCheck, PasswordCheck, ForbiddenCheck,
                                  UsernameTakenCheck, EmailLengthCheck,
                                  UsernameLengthCheck, PasswordLengthCheck)


class RegisterForm(FlaskForm):
    """Register form for auth page."""
    email = EmailField(
        label="Email",
        render_kw={"placeholder": "Email", "autofocus": True},
        validators=[
            DataRequired(message="Email is required"),
            Email(message="Invalid email"),
            EmailTakenCheck(),
            EmailLengthCheck(),
            ForbiddenCheck(),
        ]
    )
    username = StringField(
        label="Username",
        render_kw={"placeholder": "Username"},
        validators=[
            DataRequired(message="Username is required"),
            UsernameTakenCheck(),
            UsernameLengthCheck(),
            ForbiddenCheck(),
        ]
    )
    password = PasswordField(
        label="Password",
        render_kw={"placeholder": "Password"},
        validators=[
            DataRequired(message="Password is required"),
            EqualTo(fieldname="confirm_password", message="Passwords must match"),
            PasswordCheck(),
            PasswordLengthCheck(),
        ]
    )
    confirm_password = PasswordField(
        label="Confirm password",
        render_kw={"placeholder": "Confirm password"},
        validators=[
            DataRequired(message="Confirm is required"),
            EqualTo(fieldname="password", message="Passwords must match"),
            PasswordCheck(),
            PasswordLengthCheck(),
        ]
    )
    form_type = HiddenField(default="register")
    submit = SubmitField(label="Register")


class LoginForm(FlaskForm):
    """Login form for auth page."""
    email_or_uname = EmailField(
        label="Email or username",
        render_kw={"placeholder": "Email or username", "autofocus": True},
        validators=[
            DataRequired(message="Email or username is required"),
        ]
    )
    password = PasswordField(
        label="Password",
        render_kw={"placeholder": "Password"},
        validators=[
            DataRequired(message="Password is required"),
        ]
    )
    remember = BooleanField("Remember me")
    form_type = HiddenField(default="login")
    submit = SubmitField(label="Login")


class FastLoginForm(FlaskForm):
    """Fast login form for auth page."""
    fast_name = StringField(
        label="Name",
        render_kw={"placeholder": "Fast"},
        validators=[
            DataRequired(message="Name is required"),
        ]
    )
    fast_code = PasswordField(
        label="Login",
        render_kw={
            "placeholder": "Login",
            "inputmode": "numeric",
        },
        validators=[
            DataRequired(message="Code is required"),
        ]
    )
    form_type = HiddenField(default="fast_login")
    submit = SubmitField(label="Go")


class RequestResetForm(FlaskForm):
    """Request reset password form for auth page."""
    email = EmailField(
        label="Email",
        render_kw={"placeholder": "Example@example.com", "autofocus": True},
        validators=[
            DataRequired(message="Email is required"),
            Email(message="Invalid email"),
            EmailLengthCheck(),
        ]
    )
    form_type = HiddenField(default="request_reset")
    submit = SubmitField(label="Request")


class SetPasswordForm(FlaskForm):
    """Reset password form for auth page."""
    password = PasswordField(
        label="Password",
        render_kw={"placeholder": "Password", "autofocus": True},
        validators=[
            DataRequired(message="Password is required"),
            PasswordCheck(),
            PasswordLengthCheck(),
        ]
    )
    confirm_password = PasswordField(
        label="Re-type password",
        render_kw={"placeholder": "Re-type password"},
        validators=[
            DataRequired(message="Password is required"),
            EqualTo(fieldname="password"),
            PasswordCheck(),
            PasswordLengthCheck(),
        ]
    )
    form_type = HiddenField(default="password")
    submit = SubmitField(label="Set")


class ResetPasswordForm(FlaskForm):
    """Reset password form for auth page."""
    password = PasswordField(
        label="Password",
        render_kw={"placeholder": "Password", "autofocus": True},
        validators=[
            DataRequired(message="Password is required"),
            EqualTo(fieldname="confirm_password", message="Passwords must match"),
            PasswordCheck(),
            PasswordLengthCheck(),
        ]
    )
    confirm_password = PasswordField(
        label="Re-type password",
        render_kw={"placeholder": "Re-type password"},
        validators=[
            DataRequired(message="Password is required"),
            EqualTo(fieldname="password"),
            PasswordCheck(),
            PasswordLengthCheck(),
        ]
    )
    form_type = HiddenField(default="password")
    submit = SubmitField(label="Reset")
