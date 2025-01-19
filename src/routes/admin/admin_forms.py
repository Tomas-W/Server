from flask_wtf import FlaskForm
from wtforms import (
    BooleanField,
    EmailField,
    FileField,
    HiddenField,
    PasswordField,
    SelectField,
    StringField,
    SubmitField,
    TextAreaField,
)
from wtforms.validators import EqualTo

from src.utils.form_utils import (
    AboutMeLengthCheck,
    DisplayNameTakenCheck,
    EmailCheck,
    EmailLengthCheck,
    EmailTakenCheck,
    IsEmployeeCheck,
    FastCodeCheck,
    FastCodeLengthCheck,
    FastNameLengthCheck,
    FieldRequired,
    ForbiddenCheck,
    ImageUploadCheck,
    PasswordCheck,
    PasswordLengthCheck,
    UsernameLengthCheck,
    UsernameTakenCheck,
    VerifyEmailCheck,
)

from config.settings import (
    FORM,
    MESSAGE,
)


class VerifyEmailForm(FlaskForm):
    """
    Used on admin.user_admin page to verify email.
    Placeholder may be overwritten in html by current_user's email.
    If field is empty, current user's email is used.
    
    Fields:
    - EMAIL [EmailField]
    - FORM_TYPE [HiddenField]
    """
    #  Placeholder is overwritten in html by current_user's data
    #  If field is empty, current user's email is used.
    email = EmailField(
        label="Email",
        render_kw={"placeholder": "Example@example.com"},
        validators=[
            VerifyEmailCheck(),
        ]
    )
    form_type = HiddenField(default=FORM.VERIFY)
    submit = SubmitField(label="Verify")


class AuthenticationForm(FlaskForm):
    """
    Used on admin.user_admin page to update user's auth data.
    Allows empty fields for individual updates.
    Username, email and fast name placeholders
     may be overwritten in html by current_user's data.
    
    Fields:
    - EMAIL [EmailField] [Optional]
    - USERNAME [StringField] [Optional]
    - PASSWORD [PasswordField] [Optional]
    - CONFIRM_PASSWORD [PasswordField] [Optional]
    - FAST_NAME [StringField] [Optional]
    - FAST_CODE [PasswordField] [Optional]
    - FORM_TYPE [HiddenField]
    """
    #  Username, email and fast name placeholders
    #  are overwritten in html by current_user's data
    email = EmailField(
        label="email",
        render_kw={"placeholder": "example@example.com"},
        validators=[
            EmailCheck(admin=True),
            EmailLengthCheck(admin=True),
            EmailTakenCheck(),
            ForbiddenCheck(),
        ]
    )
    username = StringField(
        label="username",
        render_kw={"placeholder": "username"},
        validators=[
            UsernameLengthCheck(admin=True),
            UsernameTakenCheck(),
            ForbiddenCheck(),
        ]
    )
    password = PasswordField(
        label="password",
        render_kw={},
        validators=[
            PasswordCheck(admin=True),
            PasswordLengthCheck(admin=True),
            EqualTo(fieldname="confirm_password", message=MESSAGE.PWD_MATCH),
        ]
    )
    confirm_password = PasswordField(
        label="confirm password",
        render_kw={},
        validators=[
            PasswordCheck(admin=True),
            PasswordLengthCheck(admin=True),
            EqualTo(fieldname="password", message=MESSAGE.PWD_MATCH),
        ]
    )
    fast_name = StringField(
        label="fast name",
        render_kw={"placeholder": "fast name"},
        validators=[
            FastNameLengthCheck(admin=True),
            ForbiddenCheck(),
        ]
    )
    fast_code = PasswordField(
        label="fast code",
        render_kw={"inputmode": "numeric"},
        validators=[
            FastCodeCheck(admin=True),
            FastCodeLengthCheck(admin=True),
        ]
    )
    form_type = HiddenField(default=FORM.AUTHENTICATION)
    submit = SubmitField(label="Update")


class ProfileForm(FlaskForm):
    """
    Used on admin.user_admin page to update users' profile data.
    Allows empty fields for individual updates.
    Placeholder may be overwritten in html by current_user's data.
    
    Fields:
    - DISPLAY_NAME [StringField] [Optional]
    - COUNTRY [SelectField] [Optional]
    - PROFILE_ICON [StringField] [Optional]
    - PROFILE_PICTURE [FileField] [Optional]
    - ABOUT_ME [TextAreaField] [Optional]
    - FORM_TYPE [HiddenField]
    """
    display_name = StringField(
        label="display name",
        render_kw={"placeholder": "display name"},
        validators=[
            DisplayNameTakenCheck(),
            UsernameLengthCheck(admin=True),
            ForbiddenCheck(),
        ]
    )
    country = SelectField(
        label="country",
        choices=FORM.COUNTRY_CHOICES,
        render_kw={"style": "cursor: pointer;"},
    )
    profile_icon = StringField(
        label="profile icon",
        render_kw={"placeholder": "[ click to select ]",
                   "disabled": True},
    )
    profile_picture = FileField(
        label="profile picture",
        render_kw={"style": "opacity: 0; cursor: pointer;"},
        validators=[
            ImageUploadCheck(),
        ]
    )
    about_me = TextAreaField(
        label="about me",
        render_kw={
            "placeholder": "about me",
            "style": "resize: none; height: 200px; position: relative;"
        },
        validators=[
            ForbiddenCheck(),
            AboutMeLengthCheck(),
        ]
    )
    form_type = HiddenField(default=FORM.PROFILE)
    submit = SubmitField(label="Update")


class NotificationsForm(FlaskForm):
    """
    Used on admin.user_admin page to update user's notification settings.
    """
    news_notifications = BooleanField(label="news notifications")
    comment_notifications = BooleanField(label="comment notifications")
    bakery_notifications = BooleanField(label="bakery notifications")
    form_type = HiddenField(default=FORM.NOTIFICATIONS)
    submit = SubmitField(label="Update")


class RequestEmployeeForm(FlaskForm):
    """
    Used on admin.user_admin page to request Employee access.
    """
    employee_name = StringField(
        label="Name",
        render_kw={"placeholder": "[ please enter full name ]"},
        validators=[
            IsEmployeeCheck(),
            FieldRequired(),
        ]
    )
    code = StringField(
        label="Code",
        render_kw={"placeholder": "[ 5-digit access code ]"},
        validators=[
            FastCodeCheck(),
            FastCodeLengthCheck(),
        ]
    )
    form_type = HiddenField(default=FORM.REQUEST_EMPLOYEE)
    submit = SubmitField(label="Request")
    