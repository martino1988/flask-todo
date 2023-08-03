from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import InputRequired


class ShoppingListForm(FlaskForm):
    listname = StringField(validators=[InputRequired()])
    submit = SubmitField()

class ItemForm(FlaskForm):
    itemname = StringField('item_name',validators=[InputRequired()], render_kw={'autofocus': True})
    itemcontent = TextAreaField('item_content',validators=[InputRequired()], render_kw={'autofocus': False})
    submit = SubmitField()

