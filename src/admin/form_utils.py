from flask_wtf import FlaskForm
from wtforms.fields.core import Field
from wtforms.validators import ValidationError


class NewsCheck:
    """Validates text by checking forbidden words and characters."""
    def __init__(self, banned_words: list, banned_chars: list, message=None) -> None:
        self.banned_words = banned_words
        self.banned_chars = banned_chars

        if not message:
            message = "Invalid username and or characters"
        self.message = message

    def __call__(self, form: FlaskForm, field: Field) -> None:
        if any(word.lower() in field.data.lower() for word in self.banned_words):
            raise ValidationError(self.message)
        if any(char in field.data for char in self.banned_chars):
            raise ValidationError(self.message)
