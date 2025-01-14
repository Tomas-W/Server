import calendar

from flask_wtf import FlaskForm
from wtforms import (
    BooleanField,
    EmailField,
    HiddenField,
    SelectField,
    StringField,
    SubmitField,
)
from wtforms.validators import DataRequired

from src.utils.form_utils import (
    EmailCheck,
    EmployeeNameCheck,
)

from config.settings import FORM


class ScheduleRequestForm(FlaskForm):
    name = StringField(
        label="Name",
        render_kw={"placeholder": "name as on schedule"},
        validators=[
            EmployeeNameCheck(),
            DataRequired(),
        ]
    )
    email = EmailField(
        label="Email",
        render_kw={"placeholder": "account email"},
        validators=[
            EmailCheck(),
        ]
    )
    form_type = HiddenField(default=FORM.SCHEDULE_REQUEST)
    submit = SubmitField(label="Request")


class AddEmployeeForm(FlaskForm):
    name = StringField(
        label="Name",
        render_kw={"placeholder": "name"},
        validators=[
            EmployeeNameCheck(),
            DataRequired(),
        ]
    )
    email = EmailField(
        label="Email",
        render_kw={"placeholder": "email"},
        validators=[
            EmailCheck(),
        ]
    )
    is_verified = BooleanField(
        label="Is verified",
    )
    form_type = HiddenField(default=FORM.ADD_EMPLOYEE)
    submit = SubmitField(label="Add")


class CalendarForm(FlaskForm):
    month = SelectField(
        label="Month",
        choices=[(i, calendar.month_name[i]) for i in range(1, 13)],
    )
    year = SelectField(
        label="Year",
        choices=[(i, i) for i in range(2024, 2026)],
    )
    form_type = HiddenField(default=FORM.SCALENDAR_FORM_TYPE)
    submit = SubmitField(label="Show")
