from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, EmailField, PasswordField, BooleanField, HiddenField
from wtforms.validators import DataRequired, Length, Email, EqualTo

from config.settings import required_password_symbols
from src.auth.form_utils import EmailCheck, PasswordCheck, ForbiddenCheck


class RegisterForm(FlaskForm):
    """Register form for auth page."""
    email = EmailField(
        label="Email",
        render_kw={"placeholder": "Email", "autofocus": True},
        validators=[
            DataRequired("Email is required"),
            Email("Invalid email"),
            Length(min=1, max=75, message="Email too long"),
            EmailCheck(register=True, message="Email already registered"),
            ForbiddenCheck(),
        ]
    )
    username = StringField(
        label="Username",
        render_kw={"placeholder": "Username"},
        validators=[
            DataRequired(message="Username is required"),
            Length(min=4, max=20, message="Length must be 4 - 20"),
            ForbiddenCheck(),
        ]
    )
    password = PasswordField(
        label="Password",
        render_kw={"placeholder": "Password"},
        validators=[
            DataRequired(message="Password is required"),
            Length(min=6, max=18, message="Length must be 6 - 18"),
            PasswordCheck(required_symbols=required_password_symbols, message=None),
        ]
    )
    password2 = PasswordField(
        label="Re-type Password",
        render_kw={"placeholder": "Re-type password"},
        validators=[
            DataRequired(message="Password is required"),
            Length(min=6, max=18, message="Length must be 6 - 18"),
            EqualTo(fieldname="password", message="Passwords must match"),
            PasswordCheck(required_symbols=required_password_symbols, message=None),
        ]
    )
    form_type = HiddenField(default="register")
    submit = SubmitField(label="Register")


class LoginForm(FlaskForm):
    """Login form for auth page."""
    email_or_uname = EmailField(
        label="Email or username",
        render_kw={"placeholder": "Email or username"},
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
            Length(min=4, max=16, message="Length must be 4 - 16"),
        ]
    )
    fast_code = PasswordField(
        label="Login",
        render_kw={"placeholder": "Login"},
        validators=[
            DataRequired(message="Code is required"),
            Length(min=5, max=5, message="Code must be 5 characters"),
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
            Length(min=1, max=75, message="Email too long"),
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
            Length(min=6, max=18, message="Length must be 6 - 18"),
            PasswordCheck(required_symbols=required_password_symbols, message=None),
        ]
    )
    password2 = PasswordField(
        label="Re-type password",
        render_kw={"placeholder": "Re-type password"},
        validators=[
            DataRequired(message="Password is required"),
            Length(min=6, max=18, message="Length must be 6 - 18"),
            EqualTo(fieldname="password"),
            PasswordCheck(required_symbols=required_password_symbols, message=None),
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
            DataRequired("Password is required"),
            Length(min=6, max=18, message="Length must be 6 - 18 characters"),
            PasswordCheck(required_symbols=required_password_symbols, message=None),
        ]
    )
    password2 = PasswordField(
        label="Re-type password",
        render_kw={"placeholder": "Re-type password"},
        validators=[
            DataRequired(message="Password is required"),
            Length(min=6, max=18, message="Length must be 6 - 18"),
            EqualTo(fieldname="password"),
            PasswordCheck(required_symbols=required_password_symbols, message=None),
        ]
    )
    form_type = HiddenField(default="password")
    submit = SubmitField(label="Reset")
    