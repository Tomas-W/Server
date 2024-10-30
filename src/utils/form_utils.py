import re
from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms.fields import Field
from wtforms.validators import ValidationError

from src.extensions import server_db_

from src.models.auth_model.auth_mod import User

from config.settings import (banned_words_list, banned_characters_list,
                             required_password_symbols, MIN_COMMENT_LENGTH,
                             MAX_COMMENT_LENGTH)
from config.settings import (MIN_USERNAME_LENGTH, MAX_USERNAME_LENGTH,
                             MIN_PASSWORD_LENGTH, MAX_PASSWORD_LENGTH,
                             MIN_EMAIL_LENGTH, MAX_EMAIL_LENGTH,
                             MIN_FAST_NAME_LENGTH, MAX_FAST_NAME_LENGTH,
                             FAST_CODE_LENGTH, MIN_NEWS_TITLE_LENGTH,
                             MAX_NEWS_TITLE_LENGTH, MIN_NEWS_CONTENT_LENGTH,
                             MAX_NEWS_CONTENT_LENGTH, MIN_COMMENT_TITLE_LENGTH,
                             MAX_COMMENT_TITLE_LENGTH, MIN_COMMENT_LENGTH,
                             MAX_COMMENT_LENGTH)


class VerifyEmailCheck:
    """
    Validates email by checking if it's:
    - empty -> use current user's email
    - valid -> regex check
    - length -> length check if not empty
    """
    def __init__(self) -> None:
        self.invalid_message = "Invalid email"
        self.min_length_message = f"Min. {MIN_EMAIL_LENGTH} characters"
        self.max_length_message = f"Max. {MAX_EMAIL_LENGTH} characters"
        

    def __call__(self, form: FlaskForm, field: Field) -> None:
        if not field.data:
            field.data = current_user.email
            return
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', field.data):
            raise ValidationError(self.invalid_message)
        if len(field.data) < MIN_EMAIL_LENGTH:
            raise ValidationError(self.min_length_message)
        if len(field.data) > MAX_EMAIL_LENGTH:
            raise ValidationError(self.max_length_message)


class EmailCheck:
    """Validates email by checking if it's valid."""

    def __init__(self, admin: bool = False) -> None:
        self.admin = admin
        self.invalid_message = "Invalid email"

    def __call__(self, form: FlaskForm, field: Field) -> None:
        if self.admin and not field.data:
            return
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', field.data):
            raise ValidationError(self.invalid_message)
        
        
class EmailTakenCheck:
    """Validates email by checking if it's registered or not."""

    def __init__(self, admin: bool = False) -> None:
        self.message = "Email already registered"
        self.admin = admin

    def __call__(self, form: FlaskForm, field: Field) -> None:
        if self.admin:
            if not field.data:
                return
            elif field.data == current_user.email:
                return
        
        user = server_db_.session.execute(
            server_db_.select(User).filter_by(email=field.data)
        ).scalar_one_or_none()
        if user:
            raise ValidationError(self.message)


class EmailLengthCheck:
    """Validates email by checking length."""

    def __init__(self, admin: bool = False) -> None:
        self.admin = admin
        self.min_length_message = f"Min. {MIN_EMAIL_LENGTH} characters"
        self.max_length_message = f"Max. {MAX_EMAIL_LENGTH} characters"

    def __call__(self, form: FlaskForm, field: Field) -> None:
        if self.admin and not field.data:
            return
        if len(field.data) < MIN_EMAIL_LENGTH:
            raise ValidationError(self.min_length_message)
        if len(field.data) > MAX_EMAIL_LENGTH:
            raise ValidationError(self.max_length_message)


class UsernameTakenCheck:
    def __init__(self, admin: bool = False) -> None:
        self.message = "Username already registered"
        self.admin = admin

    def __call__(self, form: FlaskForm, field: Field) -> None:
        if self.admin:
            if not field.data:
                return
            elif current_user.username == field.data:
                return
        
        user = server_db_.session.execute(
            server_db_.select(User).filter_by(username=field.data)
        ).scalar_one_or_none()
        if user:
            raise ValidationError(self.message)


class UsernameLengthCheck:
    """Validates username by checking length."""
    
    def __init__(self, admin: bool = False) -> None:
        self.admin = admin
        self.min_length_message = f"Min. {MIN_USERNAME_LENGTH} characters"
        self.max_length_message = f"Max. {MAX_USERNAME_LENGTH} characters"

    def __call__(self, form: FlaskForm, field: Field) -> None:
        if self.admin and not field.data:
            return
        if len(field.data) < MIN_USERNAME_LENGTH:
            raise ValidationError(self.min_length_message)
        if len(field.data) > MAX_USERNAME_LENGTH:
            raise ValidationError(self.max_length_message)


class PasswordCheck:
    """Validates password by checking requirements."""

    def __init__(self, admin: bool = False) -> None:
        self.admin = admin
        self.symbols = required_password_symbols
        self.special_char_message = "One special character required"
        self.capital_letter_message = "One capital letter required"
        self.lower_letter_message = "One lower case letter required"

    def __call__(self, form: FlaskForm, field: Field) -> None:
        if self.admin and not field.data:
            return
        
        if not any(sym in field.data for sym in self.symbols):
            raise ValidationError(self.special_char_message)
        if not any(c.isupper() for c in field.data):
            raise ValidationError(self.capital_letter_message)
        if not any(c.islower() for c in field.data):
            raise ValidationError(self.lower_letter_message)


class PasswordLengthCheck:
    """Validates password by checking length."""

    def __init__(self, admin: bool = False) -> None:
        self.admin = admin
        self.min_length_message = f"Min. {MIN_PASSWORD_LENGTH} characters"
        self.max_length_message = f"Max. {MAX_PASSWORD_LENGTH} characters"

    def __call__(self, form: FlaskForm, field: Field) -> None:
        if self.admin and not field.data:
            return
        if len(field.data) < MIN_PASSWORD_LENGTH:
            raise ValidationError(self.min_length_message)
        if len(field.data) > MAX_PASSWORD_LENGTH:
            raise ValidationError(self.max_length_message)


class FastNameLengthCheck:
    """Validates fast name by checking length."""
    
    def __init__(self, admin: bool = False) -> None:
        self.admin = admin
        self.min_length_message = f"Min. {MIN_FAST_NAME_LENGTH} characters"
        self.max_length_message = f"Max. {MAX_FAST_NAME_LENGTH} characters"

    def __call__(self, form: FlaskForm, field: Field) -> None:
        if self.admin and not field.data:
            return
        if len(field.data) < MIN_FAST_NAME_LENGTH:
            raise ValidationError(self.min_length_message)
        if len(field.data) > MAX_FAST_NAME_LENGTH:
            raise ValidationError(self.max_length_message)


class FastCodeCheck:
    """Validates fast code by checking if it's an integer."""
    
    def __init__(self, admin: bool = False) -> None:
        self.admin = admin
        self.message = "Must be numeric"

    def __call__(self, form: FlaskForm, field: Field) -> None:
        if self.admin and not field.data:
            return
        if not field.data.isdigit():
            raise ValidationError(self.message)

class FastCodeLengthCheck:
    """Validates fast code by checking length."""
    
    def __init__(self, admin: bool = False) -> None:
        self.admin = admin
        self.message = f"Must be {FAST_CODE_LENGTH} characters"

    def __call__(self, form: FlaskForm, field: Field) -> None:
        if self.admin and not field.data:
            return
        if len(field.data) != FAST_CODE_LENGTH:
            raise ValidationError(self.message)


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


class NewsTitleLengthCheck:
    """Validates news title by checking length."""

    def __init__(self) -> None:
        self.min_length_message = f"Min. {MIN_NEWS_TITLE_LENGTH} characters"
        self.max_length_message = f"Max. {MAX_NEWS_TITLE_LENGTH} characters"

    def __call__(self, form: FlaskForm, field: Field) -> None:
        if len(field.data) < MIN_NEWS_TITLE_LENGTH:
            raise ValidationError(self.min_length_message)
        if len(field.data) > MAX_NEWS_TITLE_LENGTH:
            raise ValidationError(self.max_length_message)


class NewsContentLengthCheck:
    """Validates news content by checking length."""

    def __init__(self) -> None:
        self.min_length_message = f"Min. {MIN_NEWS_CONTENT_LENGTH} characters"
        self.max_length_message = f"Max. {MAX_NEWS_CONTENT_LENGTH} characters"

    def __call__(self, form: FlaskForm, field: Field) -> None:
        if len(field.data) < MIN_NEWS_CONTENT_LENGTH:
            raise ValidationError(self.min_length_message)
        if len(field.data) > MAX_NEWS_CONTENT_LENGTH:
            raise ValidationError(self.max_length_message)


class CommentTitleLengthCheck:
    """Validates comment title by checking length."""

    def __init__(self) -> None:
        self.max_length_message = f"Max. {MAX_COMMENT_TITLE_LENGTH} characters"

    def __call__(self, form: FlaskForm, field: Field) -> None:
        if len(field.data) > MAX_COMMENT_TITLE_LENGTH:
            raise ValidationError(self.max_length_message)


class CommentLengthCheck:
    """Validates comment by checking length."""

    def __init__(self) -> None:
        self.min_length_message = f"Min. {MIN_COMMENT_LENGTH} characters"
        self.max_length_message = f"Max. {MAX_COMMENT_LENGTH} characters"

    def __call__(self, form: FlaskForm, field: Field) -> None:
        if len(field.data) < MIN_COMMENT_LENGTH:
            raise ValidationError(self.min_length_message)
        if len(field.data) > MAX_COMMENT_LENGTH:
            raise ValidationError(self.max_length_message)
