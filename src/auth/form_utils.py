from flask_wtf import FlaskForm
from wtforms.fields.core import Field
from wtforms.validators import ValidationError

from src.models.auth_mod import User


class UsernameCheck:
    """Validates username by checking forbidden words and characters."""
    def __init__(self, banned_words: list, banned_chars: list, message=None) -> None:
        self.banned_words = banned_words
        self.banned_chars = banned_chars

        if not message:
            message = "Invalid username and or characters"
        self.message = message

    def __call__(self, form: FlaskForm, field: Field) -> None:
        if field.data.lower() in (word.lower() for word in self.banned_words):
            raise ValidationError(self.message)
        if len([x for x in list(self.banned_chars) if x in field.data]):
            raise ValidationError(self.message)


class PasswordCheck:
    """Validates password by checking requirements."""
    def __init__(self, required_symbols: list | str, message: str | None = None) -> None:
        self.symbols = required_symbols

        if not message:
            message = "Password requirements not met"
        self.message = message

    def __call__(self, form: FlaskForm, field: Field) -> None:
        if not any(sym in field.data for sym in self.symbols):
            raise ValidationError("At least one special character required")

        if field.data == field.data.lower() or \
                field.data == field.data.upper():
            raise ValidationError("At least one upper and one lower case "
                                  "character required")


class EmailCheck:
    """Validates email by checking is registered or not."""
    def __init__(self, register: bool = False, message: str | None = None) -> None:
        self.register = register

        if not message:
            message = "Email unknown or already registered"
        self.message = message

    def __call__(self, form: FlaskForm, field: Field) -> None:
        user = User.query.filter_by(email=field.data).first()
        if user:
            if self.register:
                raise ValidationError(self.message)

        if not user and not self.register:
            ValidationError(self.message)
