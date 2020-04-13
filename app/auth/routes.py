from app.models import User, Permission, Role
from flask import render_template, Response, redirect, url_for, flash,request, current_app, g
from flask_login import current_user, login_user, logout_user, login_required
from .. import db
from . import auth
from .forms import LoginForm, RegistrationForm
from werkzeug.urls import url_parse

import os
@auth.before_app_request
def before_request():
    g.user = current_user

#initial roles
@auth.before_app_first_request
def insert_roles():
    roles = {
            'Moderator': [Permission.VIEW, Permission.CREATE, Permission.MODERATE],
            'Administrator': [Permission.VIEW, Permission.CREATE, Permission.MODERATE, Permission.ADMIN],
        }
    default_role = 'Moderator'
    for r in roles:
        role = Role.query.filter_by(name=r).first()
        if role is None:
            role = Role(name=r)
        role.reset_permissions()
        for perm in roles[r]:
            role.add_permission(perm)
        role.default = (role.name == default_role)
        db.session.add(role)
    db.session.commit()


#initial roles
@auth.before_app_first_request
def create_admin():

    admin_role = Role.query.filter_by(name='Administrator').first()

    if User.query.filter_by(login= current_app.config['SYSTEM_ADMIN']).first() is  None:

        admin = User(login=current_app.config['SYSTEM_ADMIN'], username=current_app.config['SYSTEM_ADMIN_NAME'],\
                 role_id= admin_role.id, password= current_app.config['SYSTEM_ADMIN_PASSWORD'])

        db.session.add(admin)
        db.session.commit()



#user login/log out manager
@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.moderator', _external=True))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(login=form.username.data).first()
        if user is None or not user.verify_password(form.password.data):
            flash('Неверное имя пользователя или пароль')
            return redirect("https://digital.spmi.ru/mining_foods/auth/login")
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = "https://digital.spmi.ru/mining_foods/"+next_page
        return redirect(next_page)
    return render_template('login.html', title='Вход', form=form)


@auth.route('/logout')
def logout():
    logout_user()
    return redirect("https://digital.spmi.ru/mining_foods/auth/login")


@auth.route("/users", methods=['GET','POST'])
@login_required
def users():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(login=form.login.data, username=form.username.data, password=form.password2.data )
        db.session.add(user)
        db.session.commit()
        return redirect("https://digital.spmi.ru/mining_foods/auth/users")

    return render_template('users.html', form = form)
