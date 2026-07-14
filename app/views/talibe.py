"""Blueprint Talibé : cycle CRUD complet + recherche + export CSV."""
from flask import Blueprint, render_template, redirect, url_for, request, flash

from app.extension import db
from app.models.talibe import Talibe
from app.models.classe import Classe
from app.forms.talibe import TalibeForm
from app.exceptions import TalibeIntrouvableException, TalibeDejaExistantException
from app.utils.csv_exporter import exporter_csv

bp_talibes = Blueprint('talibes', __name__, url_prefix='/talibes')


def _charger_choix_classes(form):
    """Alimente le SelectField classe depuis la base de données."""
    form.classe_code.choices = [
        (c.code, c.libelle) for c in Classe.query.order_by(Classe.libelle).all()
    ]


@bp_talibes.route('/')
def lister():
    q = request.args.get('q', '').strip()
    classe_code = request.args.get('classe', '').strip()

    query = Talibe.query
    if classe_code:
        query = query.filter_by(classe_code=classe_code)
    if q:
        query = query.filter(
            Talibe.nom.ilike(f'%{q}%')
            | Talibe.prenom.ilike(f'%{q}%')
            | Talibe.matricule.ilike(f'%{q}%')
        )
    talibes = query.order_by(Talibe.nom).all()
    classes = Classe.query.order_by(Classe.libelle).all()
    return render_template('talibes/liste.html', talibes=talibes, classes=classes, q=q,
                            classe_code=classe_code)


@bp_talibes.route('/nouveau', methods=['GET', 'POST'])
def creer():
    form = TalibeForm()
    _charger_choix_classes(form)

    if form.validate_on_submit():
        try:
            if db.session.get(Talibe, form.matricule.data):
                raise TalibeDejaExistantException(form.matricule.data)

            talibe = Talibe(
                matricule=form.matricule.data,
                prenom=form.prenom.data,
                nom=form.nom.data,
                date_naissance=form.date_naissance.data,
                nom_tuteur=form.nom_tuteur.data,
                telephone_tuteur=form.telephone_tuteur.data,
                classe_code=form.classe_code.data,
            )
            db.session.add(talibe)
            db.session.commit()
            flash('Talibé ajouté avec succès.', 'success')
            return redirect(url_for('talibes.lister'))
        except TalibeDejaExistantException as e:
            flash(str(e), 'danger')

    return render_template('talibes/formulaire.html', form=form, talibe=None)


@bp_talibes.route('/<matricule>/modifier', methods=['GET', 'POST'])
def modifier(matricule):
    talibe = db.session.get(Talibe, matricule)
    if not talibe:
        raise TalibeIntrouvableException(matricule)

    form = TalibeForm(obj=talibe)
    _charger_choix_classes(form)

    if form.validate_on_submit():
        talibe.prenom = form.prenom.data
        talibe.nom = form.nom.data
        talibe.date_naissance = form.date_naissance.data
        talibe.nom_tuteur = form.nom_tuteur.data
        talibe.telephone_tuteur = form.telephone_tuteur.data
        talibe.classe_code = form.classe_code.data
        db.session.commit()
        flash('Talibé modifié avec succès.', 'success')
        return redirect(url_for('talibes.lister'))

    return render_template('talibes/formulaire.html', form=form, talibe=talibe)


@bp_talibes.route('/<matricule>/supprimer', methods=['POST'])
def supprimer(matricule):
    talibe = db.session.get(Talibe, matricule)
    if not talibe:
        raise TalibeIntrouvableException(matricule)

    db.session.delete(talibe)  # cascade supprime automatiquement les progressions
    db.session.commit()
    flash('Talibé supprimé (et ses progressions associées).', 'success')
    return redirect(url_for('talibes.lister'))


@bp_talibes.route('/exporter')
def exporter():
    q = request.args.get('q', '').strip()
    classe_code = request.args.get('classe', '').strip()

    query = Talibe.query
    if classe_code:
        query = query.filter_by(classe_code=classe_code)
    if q:
        query = query.filter(
            Talibe.nom.ilike(f'%{q}%')
            | Talibe.prenom.ilike(f'%{q}%')
            | Talibe.matricule.ilike(f'%{q}%')
        )
    talibes = query.order_by(Talibe.nom).all()

    entetes = ['matricule', 'prenom', 'nom', 'dateNaissance', 'classe']
    lignes = [
        [
            t.matricule, t.prenom, t.nom,
            t.date_naissance.isoformat() if t.date_naissance else '',
            t.classe.libelle,
        ]
        for t in talibes
    ]
    return exporter_csv('talibes.csv', entetes, lignes)
