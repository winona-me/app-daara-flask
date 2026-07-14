from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.extension import db
from app.models.classe import Classe
from app.models.maitre import Maitre
from app.forms.classe import ClasseForm
from app.exceptions import ClasseIntrouvableException, ClasseDejaExistanteException, SuppressionImpossibleException
from app.utils.csv_exporter import exporter_csv

bp_classes = Blueprint('classes', __name__, url_prefix='/classes')


@bp_classes.route('/')
def lister():
    q = request.args.get('q', '').strip()
    query = Classe.query
    if q:
        query = query.filter(Classe.libelle.ilike(f'%{q}%'))
    classes = query.order_by(Classe.libelle).all()
    return render_template('classes/liste.html', classes=classes, q=q)


@bp_classes.route('/nouveau', methods=['GET', 'POST'])
def creer():
    form = ClasseForm()
    form.maitre_matricule.choices = [
        (m.matricule, f"{m.prenom} {m.nom}") for m in Maitre.query.order_by(Maitre.nom).all()
    ]
    if form.validate_on_submit():
        try:
            if db.session.get(Classe, form.code.data):
                raise ClasseDejaExistanteException(form.code.data)

            classe = Classe(
                code=form.code.data,
                libelle=form.libelle.data,
                niveau=form.niveau.data,
                maitre_matricule=form.maitre_matricule.data
            )
            db.session.add(classe)
            db.session.commit()
            flash('Classe ajoutée.', 'success')
            return redirect(url_for('classes.lister'))
        except ClasseDejaExistanteException as e:
            flash(str(e), 'danger')
    return render_template('classes/formulaire.html', form=form, classe=None)


@bp_classes.route('/<code>/modifier', methods=['GET', 'POST'])
def modifier(code):
    classe = db.session.get(Classe, code)
    if not classe:
        flash(str(ClasseIntrouvableException(code)), 'danger')
        return redirect(url_for('classes.lister'))

    form = ClasseForm(obj=classe)
    form.maitre_matricule.choices = [
        (m.matricule, f"{m.prenom} {m.nom}") for m in Maitre.query.order_by(Maitre.nom).all()
    ]
    if form.validate_on_submit():
        classe.libelle = form.libelle.data
        classe.niveau = form.niveau.data
        classe.maitre_matricule = form.maitre_matricule.data
        db.session.commit()
        flash('Classe modifiée.', 'success')
        return redirect(url_for('classes.lister'))
    return render_template('classes/formulaire.html', form=form, classe=classe)


@bp_classes.route('/<code>/supprimer', methods=['POST'])
def supprimer(code):
    classe = db.session.get(Classe, code)
    if not classe:
        flash(str(ClasseIntrouvableException(code)), 'danger')
        return redirect(url_for('classes.lister'))

    try:
        if classe.talibes:
            raise SuppressionImpossibleException(
                f"Impossible de supprimer {classe.libelle} : elle contient encore {len(classe.talibes)} talibé(s)."
            )
        db.session.delete(classe)
        db.session.commit()
        flash('Classe supprimée.', 'success')
    except SuppressionImpossibleException as e:
        flash(str(e), 'danger')
    return redirect(url_for('classes.lister'))


@bp_classes.route('/exporter')
def exporter():
    q = request.args.get('q', '').strip()
    query = Classe.query
    if q:
        query = query.filter(Classe.libelle.ilike(f'%{q}%'))
    classes = query.order_by(Classe.libelle).all()

    entetes = ['code', 'libelle', 'niveau', 'maitre']
    lignes = [[c.code, c.libelle, c.niveau or '', f"{c.maitre.prenom} {c.maitre.nom}"] for c in classes]
    return exporter_csv('classes.csv', entetes, lignes)