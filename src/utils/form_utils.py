import re

from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms.fields import Field
from wtforms.validators import ValidationError

from src.extensions import logger

from src.models.schedule_model.schedule_mod import Employees

from src.utils.misc_utils import crop_name

from config.settings import (
    FORM,
    MESSAGE,
    SERVER,
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
        self.invalid_message: str = MESSAGE.INVALID_EMAIL
        self.min_length_message: str = f"Min. {FORM.MIN_EMAIL} characters"
        self.max_length_message: str = f"Max. {FORM.MAX_EMAIL} characters"

    def __call__(self, form: FlaskForm, field: Field) -> None:
        if not field.data and current_user and current_user.is_authenticated:
            field.data = current_user.email
            return
        if not re.match(SERVER.EMAIL_REGEX, field.data):
            raise ValidationError(self.invalid_message)
        if len(field.data) < FORM.MIN_EMAIL:
            raise ValidationError(self.min_length_message)
        if len(field.data) > FORM.MAX_EMAIL:
            raise ValidationError(self.max_length_message)


class EmailCheck:
    """
    Validates email by checking regex.
    If admin, allows empty field.
    """
    def __init__(self, admin: bool = False) -> None:
        self.admin: bool = admin
        self.invalid_message: str = MESSAGE.INVALID_EMAIL

    def __call__(self, form: FlaskForm, field: Field) -> None:
        if self.admin and not field.data:
            return
        if not re.match(SERVER.EMAIL_REGEX, field.data):
            raise ValidationError(self.invalid_message)


class EmailTakenCheck:
    """
    Validates email by checking if it's registered or not.
    """
    def __init__(self) -> None:
        self.email_taken_message: str = MESSAGE.EMAIL_TAKEN

    def __call__(self, form: FlaskForm, field: Field) -> None:
        if current_user and current_user.is_authenticated and current_user.email == field.data:
            return
        
        from src.models.auth_model.auth_mod import User
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
        self.min_length_message: str = f"Min. {FORM.MIN_EMAIL} characters"
        self.max_length_message: str = f"Max. {FORM.MAX_EMAIL} characters"

    def __call__(self, form: FlaskForm, field: Field) -> None:
        if self.admin and not field.data:
            return
        if len(field.data) < FORM.MIN_EMAIL:
            raise ValidationError(self.min_length_message)
        if len(field.data) > FORM.MAX_EMAIL:
            raise ValidationError(self.max_length_message)


class UsernameTakenCheck:
    """
    Validates username by checking if it's registered or not.
    """
    def __init__(self) -> None:
        self.username_taken_message: str = MESSAGE.USERNAME_TAKEN

    def __call__(self, form: FlaskForm, field: Field) -> None:
        if current_user and current_user.is_authenticated and current_user.username == field.data:
            return
        
        from src.models.auth_model.auth_mod import User
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
        self.min_length_message: str = f"Min. {FORM.MIN_USERNAME} characters"
        self.max_length_message: str = f"Max. {FORM.MAX_USERNAME} characters"

    def __call__(self, form: FlaskForm, field: Field) -> None:
        if self.admin and not field.data:
            return
        if len(field.data) < FORM.MIN_USERNAME:
            raise ValidationError(self.min_length_message)
        if len(field.data) > FORM.MAX_USERNAME:
            raise ValidationError(self.max_length_message)


class PasswordCheck:
    """
    Validates password by checking requirements.
    If admin, allows empty field.
    """
    def __init__(self, admin: bool = False) -> None:
        self.admin: bool = admin
        self.symbols: list[str] = FORM.REQUIRED_SYMBOLS
        self.special_char_message: str = MESSAGE.SPECIAL_CHAR
        self.capital_letter_message: str = MESSAGE.CAPITAL_LETTER
        self.lower_letter_message: str = MESSAGE.LOWER_LETTER

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
        self.min_length_message = f"Min. {FORM.MIN_PASSWORD} characters"
        self.max_length_message = f"Max. {FORM.MAX_PASSWORD} characters"

    def __call__(self, form: FlaskForm, field: Field) -> None:
        if self.admin and not field.data:
            return
        if len(field.data) < FORM.MIN_PASSWORD:
            raise ValidationError(self.min_length_message)
        if len(field.data) > FORM.MAX_PASSWORD:
            raise ValidationError(self.max_length_message)


class FastNameLengthCheck:
    """
    Validates fast name by checking length.
    If admin, allows empty field.
    """
    def __init__(self, admin: bool = False) -> None:
        self.admin: bool = admin
        self.min_length_message: str = f"Min. {FORM.MIN_FAST_NAME} characters"
        self.max_length_message: str = f"Max. {FORM.MAX_FAST_NAME} characters"

    def __call__(self, form: FlaskForm, field: Field) -> None:
        if self.admin and not field.data:
            return
        if len(field.data) < FORM.MIN_FAST_NAME:
            raise ValidationError(self.min_length_message)
        if len(field.data) > FORM.MAX_FAST_NAME:
            raise ValidationError(self.max_length_message)


class FastCodeCheck:
    """
    Validates fast code by checking if it's an integer.
    If admin, allows empty field.
    """
    def __init__(self, admin: bool = False) -> None:
        self.admin: bool = admin
        self.message: str = MESSAGE.FAST_CODE_ERROR

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
        self.message: str = f"Must be {FORM.FAST_CODE_LENGTH} characters"

    def __call__(self, form: FlaskForm, field: Field) -> None:
        if self.admin and not field.data:
            return
        if len(field.data) != FORM.FAST_CODE_LENGTH:
            raise ValidationError(self.message)


class IsEmployeeCheck:
    """
    Validates employee_name by checking if it's in the database.
    """
    def __init__(self) -> None:
        self.message: str = MESSAGE.EMPLOYEE_NAME_ERROR

    def __call__(self, form: FlaskForm, field: Field) -> None:
        name = crop_name(field.data)
        employee: Employees | None = Employees.query.filter_by(name=name).first()
        if not employee:
            raise ValidationError(self.message)


class DisplayNameTakenCheck:
    """
    Validates display name by checking if it's registered or not.
    """
    def __init__(self) -> None:
        self.display_name_taken_message: str = MESSAGE.DISPLAY_NAME_TAKEN

    def __call__(self, form: FlaskForm, field: Field) -> None:
        if current_user and current_user.is_authenticated and current_user.display_name == field.data:
            return
        
        from src.models.auth_model.auth_mod import User
        user: User | None = User.query.filter_by(display_name=field.data).first()
        if user:
            raise ValidationError(self.display_name_taken_message)


class DisplayNameLengthCheck:
    """  
    Validates display name by checking length.
    """
    def __init__(self) -> None:
        self.min_length_message: str = f"Min. {FORM.MIN_USERNAME} characters"
        self.max_length_message: str = f"Max. {FORM.MAX_USERNAME} characters"
    
    def __call__(self, form: FlaskForm, field: Field) -> None:
        if len(field.data) < FORM.MIN_USERNAME:
            raise ValidationError(self.min_length_message)
        if len(field.data) > FORM.MAX_USERNAME:
            raise ValidationError(self.max_length_message)

class AboutMeLengthCheck:
    """
    Validates about me by checking length.
    """
    def __init__(self) -> None:
        self.min_length_message: str = f"Min. {FORM.MIN_ABOUT_ME} characters"
        self.max_length_message: str = f"Max. {FORM.MAX_ABOUT_ME} characters"

    def __call__(self, form: FlaskForm, field: Field) -> None:
        if field.data == "" or field.data is None:
            return
        if len(field.data) < FORM.MIN_ABOUT_ME:
            raise ValidationError(self.min_length_message)
        if len(field.data) > FORM.MAX_ABOUT_ME:
            raise ValidationError(self.max_length_message)


class ForbiddenCheck:
    """
    Validates text by checking forbidden words and characters.
    """
    def __init__(self, admin: bool = False) -> None:
        self.admin: bool = admin
        self.banned_words: list[str] = SERVER.BANNED_WORDS
        self.banned_chars: list[str] = SERVER.BANNED_CHARS
        self.word_message: str = MESSAGE.FORBIDDEN_WORD
        self.char_message: str = MESSAGE.FORBIDDEN_CHAR

        self.word = ""
        self.char = ""

    def __call__(self, form: FlaskForm, field: Field) -> None:
        if field.data is None:
            return
        if self._contains_banned_word(field.data):
            raise ValidationError(self.word_message + self.word)
        if not self.admin:
            if self._contains_banned_char(field.data):
                raise ValidationError(self.char_message + self.char)

    def _contains_banned_word(self, text: str) -> bool:
        for word in self.banned_words:
            if word in text.lower():
                self.word = word
                return True
        return False

    def _contains_banned_char(self, text: str) -> bool:
        for char in self.banned_chars:
            if char in text:
                self.char = char
                return True
        return False


class NewsHeaderLengthCheck:
    """
    Validates news header by checking length.
    """
    def __init__(self) -> None:
        self.min_length_message: str = f"Min. {FORM.MIN_NEWS_HEADER} characters"
        self.max_length_message: str = f"Max. {FORM.MAX_NEWS_HEADER} characters"

    def __call__(self, form: FlaskForm, field: Field) -> None:
        if len(field.data) < FORM.MIN_NEWS_HEADER:
            raise ValidationError(self.min_length_message)
        if len(field.data) > FORM.MAX_NEWS_HEADER:
            raise ValidationError(self.max_length_message)


class NewsTitleLengthCheck:
    """
    Validates news title by checking length.
    """
    def __init__(self) -> None:
        self.min_length_message: str = f"Min. {FORM.MIN_NEWS_TITLE} characters"
        self.max_length_message: str = f"Max. {FORM.MAX_NEWS_TITLE} characters"

    def __call__(self, form: FlaskForm, field: Field) -> None:
        if len(field.data) < FORM.MIN_NEWS_TITLE:
            raise ValidationError(self.min_length_message)
        if len(field.data) > FORM.MAX_NEWS_TITLE:
            raise ValidationError(self.max_length_message)


class NewsCodeCheck:
    """
    Validates news code by checking length and if it's numeric.
    """
    def __init__(self) -> None:
        self.length_message: str = MESSAGE.NEWS_CODE_LENGTH_ERROR
        self.numeric_message: str = MESSAGE.NEWS_CODE_NUMERIC_ERROR

    def __call__(self, form: FlaskForm, field: Field) -> None:
        if not field.data.isdigit():
            raise ValidationError(self.numeric_message)
        if len(field.data) != FORM.NEWS_CODE_LENGTH:
            raise ValidationError(self.length_message)


class NewsImportantLengthCheck:
    """Validates news important by checking length."""

    def __init__(self) -> None:
        self.min_length_message: str = f"Min. {FORM.MIN_NEWS_IMPORTANT} characters"
        self.max_length_message: str = f"Max. {FORM.MAX_NEWS_IMPORTANT} characters"

    def __call__(self, form: FlaskForm, field: Field) -> None:
        if len(field.data) < FORM.MIN_NEWS_IMPORTANT:
            raise ValidationError(self.min_length_message)
        if len(field.data) > FORM.MAX_NEWS_IMPORTANT:
            raise ValidationError(self.max_length_message)


class NewsLengthCheck:
    """Validates news grid columns by checking length."""
    def __init__(self) -> None:
        self.min_length_message: str = f"Min. {FORM.MIN_NEWS} characters"
        self.max_length_message: str = f"Max. {FORM.MAX_NEWS} characters"

    def __call__(self, form: FlaskForm, field: Field) -> None:
        if len(field.data) < FORM.MIN_NEWS:
            raise ValidationError(self.min_length_message)
        if len(field.data) > FORM.MAX_NEWS:
            raise ValidationError(self.max_length_message)


class CommentLengthCheck:
    """
    Validates comment by checking length.
    """
    def __init__(self) -> None:
        self.min_length_message: str = f"Min. {FORM.MIN_COMMENT} characters"
        self.max_length_message: str = f"Max. {FORM.MAX_COMMENT} characters"

    def __call__(self, form: FlaskForm, field: Field) -> None:
        if len(field.data) < FORM.MIN_COMMENT:
            raise ValidationError(self.min_length_message)
        if len(field.data) > FORM.MAX_COMMENT:
            raise ValidationError(self.max_length_message)


class ImageUploadCheck:
    """
    Validates file by checking extension and size.
    """
    def __init__(self):
        self.allowed_extensions: list[str] = SERVER.ALLOWED_FILE_EXTENSIONS
        self.max_size: int = SERVER.MAX_IMAGE_FILE_SIZE
        self.size_message: str = MESSAGE.FILE_SIZE_ERROR
        self.extension_message: str = MESSAGE.FILE_EXTENSION_ERROR

    def __call__(self, form, field):
        if field.data:
            if field.data.filename.split(".")[-1] not in self.allowed_extensions:
                raise ValidationError(self.extension_message)
            if field.data.content_length > self.max_size:
                raise ValidationError(self.size_message)


class FieldRequired:
    """
    Validates field by checking if it's required.
    """
    def __init__(self) -> None:
        self.message: str = MESSAGE.REQUIRED_FIELD

    def __call__(self, form: FlaskForm, field: Field) -> None:
        if not field.data:
            raise ValidationError(self.message)
