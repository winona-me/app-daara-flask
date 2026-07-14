from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.extension import db
from app.models.progression import Progression
from app.models.talibe import Talibe
from app.forms.progression import ProgressionForm
from app.exceptions import ProgressionIntrouvableException, ProgressionInvalideException
from app.utils.csv_exporter import exporter_csv

bp_progressions = Blueprint('progressions', __name__, url_prefix='/progressions')


@bp_progressions.route('/')
def lister():
    talibe_matricule = request.args.get('talibe', '').strip()
    query = Progression.query
    if talibe_matricule:
        query = query.filter_by(talibe_matricule=talibe_matricule)
    progressions = query.order_by(Progression.date_evaluation.desc()).all()
    talibes = Talibe.query.order_by(Talibe.nom).all()
    return render_template(
        'progressions/liste.html',
        progressions=progressions, talibes=talibes, talibe_matricule=talibe_matricule
    )


@bp_progressions.route('/nouveau', methods=['GET', 'POST'])
def creer():
    form = ProgressionForm()
    form.talibe_matricule.choices = [
        (t.matricule, f"{t.prenom} {t.nom}") for t in Talibe.query.order_by(Talibe.nom).all()
    ]
    if form.validate_on_submit():
        try:
            if form.nombre_versets.data < 0:
                raise ProgressionInvalideException("Le nombre de versets doit être positif ou nul.")
            if not form.sourate.data.strip():
                raise ProgressionInvalideException("La sourate ne peut pas être vide.")
            if not form.talibe_matricule.data:
                raise ProgressionInvalideException("Un talibé doit être renseigné.")

            progression = Progression(
                sourate=form.sourate.data,
                nombre_versets=form.nombre_versets.data,
                date_evaluation=form.date_evaluation.data,
                observations=form.observations.data,
                talibe_matricule=form.talibe_matricule.data
            )
            db.session.add(progression)
            db.session.commit()
            flash('Progression ajoutée.', 'success')
            return redirect(url_for('progressions.lister'))
        except ProgressionInvalideException as e:
            flash(str(e), 'danger')
    return render_template('progressions/formulaire.html', form=form, progression=None)


@bp_progressions.route('/<int:id>/modifier', methods=['GET', 'POST'])
def modifier(id):
    progression = db.session.get(Progression, id)
    if not progression:
        flash(str(ProgressionIntrouvableException(id)), 'danger')
        return redirect(url_for('progressions.lister'))

    form = ProgressionForm(obj=progression)
    form.talibe_matricule.choices = [
        (t.matricule, f"{t.prenom} {t.nom}") for t in Talibe.query.order_by(Talibe.nom).all()
    ]
    if form.validate_on_submit():
        try:
            if form.nombre_versets.data < 0:
                raise ProgressionInvalideException("Le nombre de versets doit être positif ou nul.")
            if not form.sourate.data.strip():
                raise ProgressionInvalideException("La sourate ne peut pas être vide.")

            progression.sourate = form.sourate.data
            progression.nombre_versets = form.nombre_versets.data
            progression.date_evaluation = form.date_evaluation.data
            progression.observations = form.observations.data
            progression.talibe_matricule = form.talibe_matricule.data
            db.session.commit()
            flash('Progression modifiée.', 'success')
            return redirect(url_for('progressions.lister'))
        except ProgressionInvalideException as e:
            flash(str(e), 'danger')
    return render_template('progressions/formulaire.html', form=form, progression=progression)


@bp_progressions.route('/<int:id>/supprimer', methods=['POST'])
def supprimer(id):
    progression = db.session.get(Progression, id)
    if not progression:
        flash(str(ProgressionIntrouvableException(id)), 'danger')
        return redirect(url_for('progressions.lister'))

    db.session.delete(progression)
    db.session.commit()
    flash('Progression supprimée.', 'success')
    return redirect(url_for('progressions.lister'))


@bp_progressions.route('/exporter')
def exporter():
    talibe_matricule = request.args.get('talibe', '').strip()
    query = Progression.query
    if talibe_matricule:
        query = query.filter_by(talibe_matricule=talibe_matricule)
    progressions = query.order_by(Progression.date_evaluation.desc()).all()

    entetes = ['id', 'sourate', 'nombreVersets', 'dateEvaluation', 'talibe']
    lignes = [
        [p.id, p.sourate, p.nombre_versets,
         p.date_evaluation.isoformat() if p.date_evaluation else '',
         f"{p.talibe.prenom} {p.talibe.nom}"]
        for p in progressions
    ]
    return exporter_csv('progressions.csv', entetes, lignes)