from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, EmailField, PasswordField
from wtforms.fields.simple import BooleanField, HiddenField
from wtforms.validators import DataRequired, Length, Email, EqualTo

from config.settings import (banned_username_words, required_password_symbols,
                             banned_username_chars)
from src.auth.form_utils import EmailCheck, UsernameCheck, PasswordCheck


class RegisterForm(FlaskForm):
    """Register form for auth page."""
    email = EmailField(
        label="Email",
        render_kw={"placeholder": "Example@example.com",
                   "autofocus": True},
        validators=[DataRequired(message="Email is required"),
                    Email(message="Invalid email address"),
                    Length(min=1, max=75,
                           message="Email must not exceed 75 char"),
                    EmailCheck(register=True,
                               message="Email already registered")
                    ])
    username = StringField(
        label="Username",
        render_kw={"placeholder": "Username"},
        validators=[DataRequired(message="Username is required"),
                    Length(min=4, max=20,
                           message="Length must be 4 - 20"),
                    UsernameCheck(
                        banned_words=banned_username_words,
                        banned_chars=banned_username_chars,
                        message="Invalid username and or characters"),
                    ])
    password = PasswordField(
        label="Password",
        render_kw={"placeholder": "Password"},
        validators=[DataRequired(message="Password is required"),
                    Length(min=6, max=18,
                           message="Length must be 8 - 24"),
                    PasswordCheck(
                        required_symbols=required_password_symbols,
                        message=None),
                    ])
    password2 = PasswordField(
        label="Re-type Password",
        render_kw={"placeholder": "Re-type password"},
        validators=[DataRequired(message="Passwords must match"),
                    Length(min=8, max=24,
                           message="Password must be 8 - 24 char"),
                    EqualTo(fieldname="password",
                            message="Passwords must match"),
                    PasswordCheck(
                        required_symbols=required_password_symbols,
                        message=None),
                    ])
    form_type = HiddenField(default="register")
    submit = SubmitField(label="Register")


class LoginForm(FlaskForm):
    """Login form for auth page."""
    email_or_uname = EmailField(label="Email or username",
                                render_kw={"placeholder": "Email or username"},
                                validators=[DataRequired(message="Email or username is"
                                                                 " required"),
                                            ])
    password = PasswordField(label="Password",
                             render_kw={"placeholder": "Password"},
                             validators=[DataRequired(message="Password is required")])
    remember = BooleanField("Remember me")
    form_type = HiddenField(default="login")

    submit = SubmitField(label="Login")


class FastLoginForm(FlaskForm):
    """Fast login form for auth page."""
    fast_name = StringField(
        label="Name",
        render_kw={"placeholder": "Fast"},
        validators=[DataRequired(message="Name is required"),
                    Length(min=4, max=16,
                           message="Length must be 4 - 16"),
                    UsernameCheck(
                        banned_words=banned_username_words,
                        banned_chars=banned_username_chars,
                        message="Invalid name and or characters"),
                    ])

    fast_code = PasswordField(label="Code",
                              render_kw={"placeholder": "Login"},
                              validators=[DataRequired(message="Code is required"),
                                          Length(min=5, max=5,
                                                 message="Code must be 5 char"),
                                          ])
    form_type = HiddenField(default="fast_login")
    submit = SubmitField(label="Go")


class EmailForm(FlaskForm):
    """Request reset password form for auth page."""
    email = EmailField(label="Email",
                       render_kw={"placeholder": "Example@example.com",
                                  "autofocus": True},
                       validators=[DataRequired(message="Email is required"),
                                   Email(message="Invalid email"),
                                   Length(min=1, max=75,
                                          message="Email must not exceed 75 char"),
                                   EmailCheck(message="Email not registered"),
                                   ])
    form_type = HiddenField(default="email")
    submit = SubmitField(label="Submit")


class PasswordForm(FlaskForm):
    """Reset password form for auth page."""
    password = PasswordField(label="Password",
                             render_kw={"placeholder": "Password",
                                        "autofocus": True},
                             validators=[DataRequired(message="Password is required"),
                                         Length(min=8, max=24,
                                                message="Password must be 8 - 24 char"),
                                         PasswordCheck(
                                             required_symbols=required_password_symbols,
                                             message=None),
                                         ])
    password2 = PasswordField(label="Re-type password",
                              render_kw={"placeholder": "Re-type password"},
                              validators=[DataRequired(message="Password is required"),
                                          Length(min=8, max=24,
                                                 message="Password must be 8 - 24 char"),
                                          EqualTo(fieldname="password"),
                                          PasswordCheck(
                                              required_symbols=required_password_symbols,
                                              message=None),
                                          ])
    form_type = HiddenField(default="password")
    submit = SubmitField(label="Reset")
