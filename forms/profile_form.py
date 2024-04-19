from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, FileField
from wtforms.validators import DataRequired, regexp


class ProfileForm(FlaskForm):
    name = StringField('Имя', validators=[DataRequired()])
    about = TextAreaField('О себе')
    photo = FileField('Фото')
    submit = SubmitField('Сохранить')

