import calendar
from flask_wtf import FlaskForm
from wtforms import (
    StringField, SubmitField, BooleanField, HiddenField, EmailField, SelectField
)
from wtforms.validators import DataRequired
from src.utils.form_utils import EmployeeNameCheck, EmailCheck
from config.settings import (
    SCHEDULE_REQUEST_FORM_TYPE, ADD_EMPLOYEE_FORM_TYPE, SCHEDULE_CALENDAR_FORM_TYPE
)

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
    form_type = HiddenField(default=SCHEDULE_REQUEST_FORM_TYPE)
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
    form_type = HiddenField(default=ADD_EMPLOYEE_FORM_TYPE)
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
    form_type = HiddenField(default=SCHEDULE_CALENDAR_FORM_TYPE)
    submit = SubmitField(label="Show")
