from flask import request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, Form
from wtforms.fields.core import DecimalField, IntegerField, SelectField
from wtforms.validators import ValidationError, DataRequired, Length
from app.models import User
import decimal

class EditProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    about_me = TextAreaField('About me',
                             validators=[Length(min=0, max=140)])
    submit = SubmitField('Submit')

    def __init__(self, original_username, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=self.username.data).first()
            if user is not None:
                raise ValidationError('Please use a different username.')

class EmptyForm(FlaskForm):
    submit = SubmitField('Submit')

class TransactionForm(FlaskForm):
    ticker = StringField('ticker', validators=[DataRequired()])
    price = DecimalField('price', places=2, rounding=decimal.ROUND_UP, validators=[DataRequired()])
    amount = IntegerField('shares', validators=[DataRequired()])
    company = StringField('company', validators=[DataRequired()])
    buy_or_sell = SelectField(u'Buy or Sell', choices=[('BUY' , 'Buy'),('SELL', 'Sell')])
    submit = SubmitField('Submit')

class SearchForm(FlaskForm):
    ticker = StringField('ticker', validators=[DataRequired(), Length(max=10)])
    submit = SubmitField('Submit')


