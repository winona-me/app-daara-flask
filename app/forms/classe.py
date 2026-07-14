from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length, Optional

class ClasseForm(FlaskForm):
    code = StringField(
        'Code',
        validators=[DataRequired(), Length(max=50)]
    )
    libelle = StringField(
        'Libellé',
        validators=[DataRequired(), Length(max=100)]
    )
    niveau = StringField(
        'Niveau',
        validators=[Optional(), Length(max=50)]
    )
    maitre_matricule = SelectField(
        'Maître',
        validators=[DataRequired()]
        # choices sera rempli dans la vue depuis la BDD
    )
    submit = SubmitField('Enregistrer')