import re
from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms.fields import Field
from wtforms.validators import ValidationError

from src.models.auth_model.auth_mod import User

from config.settings import (
    banned_words_list, banned_characters_list, REQUIRED_SYMBOLS,
    MIN_COMMENT_LENGTH, MAX_COMMENT_LENGTH
)
from config.settings import (
    MIN_USERNAME_LENGTH, MAX_USERNAME_LENGTH, MIN_PASSWORD_LENGTH, MAX_PASSWORD_LENGTH,
    MIN_EMAIL_LENGTH, MAX_EMAIL_LENGTH, MIN_FAST_NAME_LENGTH, MAX_FAST_NAME_LENGTH,
    FAST_CODE_LENGTH, MIN_NEWS_TITLE_LENGTH, MAX_NEWS_TITLE_LENGTH,
    MIN_NEWS_CONTENT_LENGTH, MAX_NEWS_CONTENT_LENGTH, MIN_COMMENT_LENGTH,
    MAX_COMMENT_LENGTH, MAX_IMAGE_FILE_SIZE, ALLOWED_FILE_EXTENSIONS,
    EMAIL_TAKEN_MSG, USERNAME_TAKEN_MSG, INVALID_EMAIL_MSG, SPECIAL_CHAR_MSG,
    CAPITAL_LETTER_MSG, LOWER_LETTER_MSG, FAST_CODE_ERROR_MSG, FORBIDDEN_WORD_MSG,
    FORBIDDEN_CHAR_MSG, FILE_SIZE_ERROR_MSG, MIN_ABOUT_ME_LENGTH, MAX_ABOUT_ME_LENGTH,
    DISPLAY_NAME_TAKEN_MSG
)


class VerifyEmailCheck:
    """
    Used for email verification.
    Validates email by checking if it's:
    - empty -> use current user's email
    - valid -> regex check
    - length -> length check if not empty
    """
    def __init__(self) -> None:
        self.invalid_message: str = INVALID_EMAIL_MSG
        self.min_length_message: str = f"Min. {MIN_EMAIL_LENGTH} characters"
        self.max_length_message: str = f"Max. {MAX_EMAIL_LENGTH} characters"

    def __call__(self, form: FlaskForm, field: Field) -> None:
        if not field.data and current_user.is_authenticated:
            field.data = current_user.email
            return
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', field.data):
            raise ValidationError(self.invalid_message)
        if len(field.data) < MIN_EMAIL_LENGTH:
            raise ValidationError(self.min_length_message)
        if len(field.data) > MAX_EMAIL_LENGTH:
            raise ValidationError(self.max_length_message)


class EmailCheck:
    """
    Validates email by checking regex.
    If admin, allows empty field.
    """
    def __init__(self, admin: bool = False) -> None:
        self.admin: bool = admin
        self.invalid_message: str = INVALID_EMAIL_MSG

    def __call__(self, form: FlaskForm, field: Field) -> None:
        if self.admin and not field.data:
            return
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', field.data):
            raise ValidationError(self.invalid_message)
        
        
class EmailTakenCheck:
    """
    Validates email by checking if it's registered or not.
    """
    def __init__(self) -> None:
        self.email_taken_message: str = EMAIL_TAKEN_MSG

    def __call__(self, form: FlaskForm, field: Field) -> None:
        if current_user.is_authenticated and current_user.email == field.data:
            return
        user: User | None = User.query.filter_by(email=field.data).first()
        if user:
            raise ValidationError(self.email_taken_message)


class EmailLengthCheck:
    """
    Validates email by checking length.
    If admin, allows empty field.
    """
    def __init__(self, admin: bool = False) -> None:
        self.admin: bool = admin
        self.min_length_message: str = f"Min. {MIN_EMAIL_LENGTH} characters"
        self.max_length_message: str = f"Max. {MAX_EMAIL_LENGTH} characters"

    def __call__(self, form: FlaskForm, field: Field) -> None:
        if self.admin and not field.data:
            return
        if len(field.data) < MIN_EMAIL_LENGTH:
            raise ValidationError(self.min_length_message)
        if len(field.data) > MAX_EMAIL_LENGTH:
            raise ValidationError(self.max_length_message)


class UsernameTakenCheck:
    """
    Validates username by checking if it's registered or not.
    """
    def __init__(self) -> None:
        self.username_taken_message: str = USERNAME_TAKEN_MSG

    def __call__(self, form: FlaskForm, field: Field) -> None:
        if current_user.is_authenticated and current_user.username == field.data:
            return
        user: User | None = User.query.filter_by(username=field.data).first()
        if user:
            raise ValidationError(self.username_taken_message)


class UsernameLengthCheck:
    """
    Validates username by checking length.
    If admin, allows empty field.
    """
    def __init__(self, admin: bool = False) -> None:
        self.admin: bool = admin
        self.min_length_message: str = f"Min. {MIN_USERNAME_LENGTH} characters"
        self.max_length_message: str = f"Max. {MAX_USERNAME_LENGTH} characters"

    def __call__(self, form: FlaskForm, field: Field) -> None:
        if self.admin and not field.data:
            return
        if len(field.data) < MIN_USERNAME_LENGTH:
            raise ValidationError(self.min_length_message)
        if len(field.data) > MAX_USERNAME_LENGTH:
            raise ValidationError(self.max_length_message)
                

class PasswordCheck:
    """
    Validates password by checking requirements.
    If admin, allows empty field.
    """
    def __init__(self, admin: bool = False) -> None:
        self.admin: bool = admin
        self.symbols: list[str] = REQUIRED_SYMBOLS
        self.special_char_message: str = SPECIAL_CHAR_MSG
        self.capital_letter_message: str = CAPITAL_LETTER_MSG
        self.lower_letter_message: str = LOWER_LETTER_MSG

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
    """
    Validates password by checking length.
    If admin, allows empty field.
    """
    def __init__(self, admin: bool = False) -> None:
        self.admin: bool = admin
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
    """
    Validates fast name by checking length.
    If admin, allows empty field.
    """
    def __init__(self, admin: bool = False) -> None:
        self.admin: bool = admin
        self.min_length_message: str = f"Min. {MIN_FAST_NAME_LENGTH} characters"
        self.max_length_message: str = f"Max. {MAX_FAST_NAME_LENGTH} characters"

    def __call__(self, form: FlaskForm, field: Field) -> None:
        if self.admin and not field.data:
            return
        if len(field.data) < MIN_FAST_NAME_LENGTH:
            raise ValidationError(self.min_length_message)
        if len(field.data) > MAX_FAST_NAME_LENGTH:
            raise ValidationError(self.max_length_message)


class FastCodeCheck:
    """
    Validates fast code by checking if it's an integer.
    If admin, allows empty field.
    """
    def __init__(self, admin: bool = False) -> None:
        self.admin: bool = admin
        self.message: str = FAST_CODE_ERROR_MSG

    def __call__(self, form: FlaskForm, field: Field) -> None:
        if self.admin and not field.data:
            return
        if not field.data.isdigit():
            raise ValidationError(self.message)


class FastCodeLengthCheck:
    """
    Validates fast code by checking length.
    If admin, allows empty field.
    """
    def __init__(self, admin: bool = False) -> None:
        self.admin: bool = admin
        self.message: str = f"Must be {FAST_CODE_LENGTH} characters"

    def __call__(self, form: FlaskForm, field: Field) -> None:
        if self.admin and not field.data:
            return
        if len(field.data) != FAST_CODE_LENGTH:
            raise ValidationError(self.message)


class DisplayNameTakenCheck:
    """
    Validates display name by checking if it's registered or not.
    """
    def __init__(self) -> None:
        self.display_name_taken_message: str = DISPLAY_NAME_TAKEN_MSG

    def __call__(self, form: FlaskForm, field: Field) -> None:
        if current_user.is_authenticated and current_user.display_name == field.data:
            return
        user: User | None = User.query.filter_by(display_name=field.data).first()
        if user:
            raise ValidationError(self.display_name_taken_message)



class AboutMeLengthCheck:
    """
    Validates about me by checking length.
    """
    def __init__(self) -> None:
        self.min_length_message: str = f"Min. {MIN_ABOUT_ME_LENGTH} characters"
        self.max_length_message: str = f"Max. {MAX_ABOUT_ME_LENGTH} characters"

    def __call__(self, form: FlaskForm, field: Field) -> None:
        if len(field.data) < MIN_ABOUT_ME_LENGTH:
            raise ValidationError(self.min_length_message)
        if len(field.data) > MAX_ABOUT_ME_LENGTH:
            raise ValidationError(self.max_length_message)


class ForbiddenCheck:
    """
    Validates text by checking forbidden words and characters.
    """
    def __init__(self) -> None:
        self.banned_words: list[str] = banned_words_list
        self.banned_chars: list[str] = banned_characters_list
        self.word_message: str = FORBIDDEN_WORD_MSG
        self.char_message: str = FORBIDDEN_CHAR_MSG

    def __call__(self, form: FlaskForm, field: Field) -> None:
        if field.data is None:
            return
        if self._contains_banned_word(field.data):
            raise ValidationError(self.word_message)
        if self._contains_banned_char(field.data):
            raise ValidationError(self.char_message)

    def _contains_banned_word(self, text: str) -> bool:
        return any(word in text.lower() for word in self.banned_words)

    def _contains_banned_char(self, text: str) -> bool:
        return any(char in text for char in self.banned_chars)


class NewsTitleLengthCheck:
    """
    Validates news title by checking length.
    """
    def __init__(self) -> None:
        self.min_length_message: str = f"Min. {MIN_NEWS_TITLE_LENGTH} characters"
        self.max_length_message: str = f"Max. {MAX_NEWS_TITLE_LENGTH} characters"

    def __call__(self, form: FlaskForm, field: Field) -> None:
        if len(field.data) < MIN_NEWS_TITLE_LENGTH:
            raise ValidationError(self.min_length_message)
        if len(field.data) > MAX_NEWS_TITLE_LENGTH:
            raise ValidationError(self.max_length_message)


class NewsContentLengthCheck:
    """Validates news content by checking length."""

    def __init__(self) -> None:
        self.min_length_message: str = f"Min. {MIN_NEWS_CONTENT_LENGTH} characters"
        self.max_length_message: str = f"Max. {MAX_NEWS_CONTENT_LENGTH} characters"

    def __call__(self, form: FlaskForm, field: Field) -> None:
        if len(field.data) < MIN_NEWS_CONTENT_LENGTH:
            raise ValidationError(self.min_length_message)
        if len(field.data) > MAX_NEWS_CONTENT_LENGTH:
            raise ValidationError(self.max_length_message)


class CommentLengthCheck:
    """
    Validates comment by checking length.
    """
    def __init__(self) -> None:
        self.min_length_message: str = f"Min. {MIN_COMMENT_LENGTH} characters"
        self.max_length_message: str = f"Max. {MAX_COMMENT_LENGTH} characters"

    def __call__(self, form: FlaskForm, field: Field) -> None:
        if len(field.data) < MIN_COMMENT_LENGTH:
            raise ValidationError(self.min_length_message)
        if len(field.data) > MAX_COMMENT_LENGTH:
            raise ValidationError(self.max_length_message)


class ImageUploadCheck:
    """
    Validates file by checking extension and size.
    """
    def __init__(self):
        self.allowed_extensions: list[str] = ALLOWED_FILE_EXTENSIONS
        self.max_size: int = MAX_IMAGE_FILE_SIZE
        self.size_message: str = FILE_SIZE_ERROR_MSG
        self.extension_message: str = "Invalid file extension"

    def __call__(self, form, field):
        if field.data:
            if field.data.filename.split(".")[-1] not in self.allowed_extensions:
                raise ValidationError(self.extension_message)
            if field.data.content_length > self.max_size:
                raise ValidationError(self.size_message)

