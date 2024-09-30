from flask_wtf import FlaskForm
from wtforms.fields import Field
from wtforms.validators import ValidationError

from config.settings import banned_words_list, banned_characters_list
from src.models.auth_mod import User
from src.extensions import server_db_


class ForbiddenCheck:
    """Validates text by checking forbidden words and characters."""

    def __init__(self) -> None:
        self.banned_words: list[str] = banned_words_list
        self.banned_chars: list[str] = banned_characters_list
        self.word_message: str = "Contains banned word"
        self.char_message: str = "Contains banned character"

    def __call__(self, form: FlaskForm, field: Field) -> None:
        if self._contains_banned_word(field.data):
            raise ValidationError(self.word_message)
        
        if self._contains_banned_char(field.data):
            raise ValidationError(self.char_message)

    def _contains_banned_word(self, text: str) -> bool:
        return any(word in text.lower() for word in self.banned_words)

    def _contains_banned_char(self, text: str) -> bool:
        return any(char in text for char in self.banned_chars)


class PasswordCheck:
    """Validates password by checking requirements."""
    def __init__(self, required_symbols: list | str, message: str | None = None) -> None:
        self.symbols = required_symbols
        self.message = message or "Password requirements not met"

    def __call__(self, form: FlaskForm, field: Field) -> None:
        if not any(sym in field.data for sym in self.symbols):
            raise ValidationError("One special character required")
        if not any(c.isupper() for c in field.data):
            raise ValidationError("One capital letter required")
        if not any(c.islower() for c in field.data):
            raise ValidationError("One lower case letter required")


class EmailCheck:
    """Validates email by checking if it's registered or not."""
    def __init__(self, register: bool = False, message: str | None = None) -> None:
        self.register = register
        self.message = message or "Email unknown or already registered"

    def __call__(self, form: FlaskForm, field: Field) -> None:
        user = server_db_.session.execute(
            server_db_.select(User).filter_by(email=field.data)
        ).scalar_one_or_none()
        if (user and self.register) or (not user and not self.register):
            raise ValidationError(self.message)
