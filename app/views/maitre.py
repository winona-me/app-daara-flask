from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.extension import db
from app.models.maitre import Maitre
from app.forms.maitre import MaitreForm
from app.exceptions import MaitreIntrouvableException, MaitreDejaExistantException, SuppressionImpossibleException
from app.utils.csv_exporter import exporter_csv

bp_maitres = Blueprint('maitres', __name__, url_prefix='/maitres')


@bp_maitres.route('/')
def lister():
    q = request.args.get('q', '').strip()
    query = Maitre.query
    if q:
        query = query.filter(
            Maitre.nom.ilike(f'%{q}%') | Maitre.prenom.ilike(f'%{q}%')
        )
    maitres = query.order_by(Maitre.nom).all()
    return render_template('maitres/liste.html', maitres=maitres, q=q)


@bp_maitres.route('/nouveau', methods=['GET', 'POST'])
def creer():
    form = MaitreForm()
    if form.validate_on_submit():
        try:
            if db.session.get(Maitre, form.matricule.data):
                raise MaitreDejaExistantException(form.matricule.data)

            maitre = Maitre(
                matricule=form.matricule.data,
                prenom=form.prenom.data,
                nom=form.nom.data,
                telephone=form.telephone.data
            )
            db.session.add(maitre)
            db.session.commit()
            flash('Maître ajouté.', 'success')
            return redirect(url_for('maitres.lister'))
        except MaitreDejaExistantException as e:
            flash(str(e), 'danger')
    return render_template('maitres/formulaire.html', form=form, maitre=None)


@bp_maitres.route('/<matricule>/modifier', methods=['GET', 'POST'])
def modifier(matricule):
    maitre = db.session.get(Maitre, matricule)
    if not maitre:
        flash(str(MaitreIntrouvableException(matricule)), 'danger')
        return redirect(url_for('maitres.lister'))

    form = MaitreForm(obj=maitre)
    if form.validate_on_submit():
        maitre.prenom = form.prenom.data
        maitre.nom = form.nom.data
        maitre.telephone = form.telephone.data
        db.session.commit()
        flash('Maître modifié.', 'success')
        return redirect(url_for('maitres.lister'))
    return render_template('maitres/formulaire.html', form=form, maitre=maitre)


@bp_maitres.route('/<matricule>/supprimer', methods=['POST'])
def supprimer(matricule):
    maitre = db.session.get(Maitre, matricule)
    if not maitre:
        flash(str(MaitreIntrouvableException(matricule)), 'danger')
        return redirect(url_for('maitres.lister'))

    try:
        if maitre.classes:
            raise SuppressionImpossibleException(
                f"Impossible de supprimer {maitre.nom} : il encadre encore {len(maitre.classes)} classe(s)."
            )
        db.session.delete(maitre)
        db.session.commit()
        flash('Maître supprimé.', 'success')
    except SuppressionImpossibleException as e:
        flash(str(e), 'danger')
    return redirect(url_for('maitres.lister'))


@bp_maitres.route('/exporter')
def exporter():
    q = request.args.get('q', '').strip()
    query = Maitre.query
    if q:
        query = query.filter(
            Maitre.nom.ilike(f'%{q}%') | Maitre.prenom.ilike(f'%{q}%')
        )
    maitres = query.order_by(Maitre.nom).all()

    entetes = ['matricule', 'prenom', 'nom', 'telephone']
    lignes = [[m.matricule, m.prenom, m.nom, m.telephone or ''] for m in maitres]
    return exporter_csv('maitres.csv', entetes, lignes)