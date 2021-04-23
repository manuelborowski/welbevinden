# -*- coding: utf-8 -*-

from flask import redirect, render_template, url_for, request
from flask_login import login_required, login_user, logout_user
from sqlalchemy import func

from app import log, db, flask_app
from . import auth
from .forms import LoginForm
from app.data.models import User
from app.presentation.layout import utils
import datetime, json

@auth.route('/', methods=['POST', 'GET'])
def login():
    form = LoginForm(request.form)
    if form.validate() and request.method == 'POST':
        user = User.query.filter_by(username=func.binary(form.username.data)).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user)
            log.info(u'user {} logged in'.format(user.username))
            user.last_login = datetime.datetime.now()
            try:
                db.session.commit()
            except Exception as e:
                log.error(u'Could not save timestamp: {}'.format(e))
                utils.flash_plus(u'Fout in database', e)
                return redirect(url_for('auth.login'))
            # Ok, continue
            return redirect(url_for('reservation.show'))
        else:
            utils.flash_plus(u'Ongeldige gebruikersnaam of paswoord')
            log.error(u'Invalid username/password')
    return render_template('auth/login.html', form=form, title='Login')


@auth.route('/logout')
@login_required
def logout():
    log.info(u'User logged out')
    logout_user()
    return redirect(url_for('auth.login'))

