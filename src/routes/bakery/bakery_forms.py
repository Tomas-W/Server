from flask_wtf import FlaskForm
from wtforms import (StringField, HiddenField, SubmitField, BooleanField,
                     SelectField
)
from config.settings import (BAKERY_SEARCH_FORM_TYPE, BAKERY_REFINE_SEARCH_FORM_TYPE,
                             NUTRI_CHOICES
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
        choices=NUTRI_CHOICES,
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
        render_kw={"placeholder": "Nasa"},
    )
    form_type = HiddenField(default=BAKERY_SEARCH_FORM_TYPE)
    submit = SubmitField("Search")
