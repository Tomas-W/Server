from flask_wtf import FlaskForm
from wtforms import (
    BooleanField,
    HiddenField,
    SelectField,
    StringField,
    SubmitField,
)

from config.settings import (
    FORM,
)


class BakerySearchForm(FlaskForm):  
    search_field = StringField(
        label="All",
        render_kw={"placeholder": "All"},
    )
    contains = StringField(
        label="Contains",
        render_kw={"placeholder": "Contains"},
    )
    may_contain = StringField(
        label="May contain",
        render_kw={"placeholder": "May contain"},
    )
    lactose_free = BooleanField(
        label="Lactose free",
        render_kw={"placeholder": "Lactose free"},
    )
    vegan = BooleanField(
        label="Vegan",
        render_kw={"placeholder": "Vegan"},
    )
    nutri_score = SelectField(
        label="Nutri score",
        choices=FORM.NUTRI_CHOICES,
        render_kw={},
    )
    min_price = StringField(
        label="Min price",
        render_kw={"placeholder": "Min price"},
    )
    max_price = StringField(
        label="Max price",
        render_kw={"placeholder": "Max price"},
    )
    nasa = StringField(
        label="Nasa",
        render_kw={"placeholder": "Nasa",
                   "inputmode": "numeric",
                   "pattern": "[0-9]*"},
    )
    form_type = HiddenField(default=FORM.BAKERY_SEARCH)
    submit = SubmitField("Search")
