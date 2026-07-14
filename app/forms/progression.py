from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, DateField, TextAreaField, IntegerField, SubmitField
from wtforms.validators import DataRequired, Length, Optional, NumberRange

class ProgressionForm(FlaskForm):
    sourate = StringField(
        'Sourate',
        validators=[DataRequired(), Length(max=100)]
    )
    nombre_versets = IntegerField(
        'Nombre de versets',
        validators=[DataRequired(), NumberRange(min=0, message="Le nombre de versets doit être positif ou nul.")]
    )
    date_evaluation = DateField(
        'Date d\'évaluation',
        validators=[Optional()]
    )
    observations = TextAreaField(
        'Observations',
        validators=[Optional()]
    )
    talibe_matricule = SelectField(
        'Talibé',
        validators=[DataRequired()]
        # choices sera rempli dans la vue depuis la BDD
    )
    submit = SubmitField('Enregistrer')