from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField, HiddenField, EmailField
from wtforms.validators import DataRequired
from src.utils.form_utils import EmployeeNameCheck, EmailCheck
from config.settings import SCHEDULE_REQUEST_FORM_TYPE, ADD_EMPLOYEE_FORM_TYPE

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
