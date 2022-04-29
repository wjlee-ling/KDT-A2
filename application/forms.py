from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired, Length

class PromptForm(FlaskForm):
    # newspaper = SelectField('언론사', choices=[('', '없음'), ('조선일보', '조선일보'), \
    #                                         ('동아일보', '동아일보'), ('중앙일보', '중앙일보'), \
    #                                         ('한겨레', '한겨레'), ('경향신문', '경향신문')])
    lead = StringField(label='입력', validators=[DataRequired(), Length(min=3, max=30)])
    submit = SubmitField(label='이어서 생성하기')
