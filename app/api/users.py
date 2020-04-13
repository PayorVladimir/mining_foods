from flask import jsonify, request, g, Response
from .. import db
from . import api
from ..models import User,Permission
from .errors import forbidden, bad_request, not_found
from flask_login import current_user, login_user, logout_user, login_required
import datetime
from .decorators import permission_required
from sqlalchemy import desc


@api.route('users/', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.ADMIN)
def get_users():
    page = request.form["page"]
    rows = request.form["rows"]

    users = User.query.paginate(page=int(page), error_out=False, per_page=int(rows)).items
    return jsonify({
        "total": len(users),
        "rows": [user.to_json() for user in users]
    })

@api.route('new_user', methods=['POST'])
@login_required
@permission_required(Permission.ADMIN)
def new_user():
    if not request.is_json:
        return bad_request("No JSON data")

    login = request.json["login"]
    if login is None or login == "":
        return bad_request("Логин не указан")
    if User.query.filter(User.login == login).first() is not None:
        return bad_request("Пользователь с таким именем уже существует")
    username = request.json["username"]
    if username is None or username == "":
        return bad_request("Имя пользователя не указано")

    if len(username) > 64:
        return bad_request("Имя пользователя не должно превышать 64 символа.")

    if len(login) > 64:
        return bad_request("Логин пользователя не должен превышать 64 символа.")

    password = request.json["password"]

    if password is None or password == "":
        return bad_request("Пароль не указан")

    user = User(login=login, username=username, password=password)



    db.session.add(user)
    db.session.commit()
    return jsonify({"message": "Пользователь успешно зарегистрирован"})


@api.route('block_user', methods=['PUT'])
@login_required
@permission_required(Permission.ADMIN)
def block_user():
    if not request.is_json:
        return bad_request("No JSON data")
    user_id = request.json["user_id"]
    

    user = User.query.get_or_404(user_id)

    if user.role.name == "Administrator":
        return bad_request("Администратора заблокировать нельзя.")
    user.is_active = False

    db.session.add(user)
    db.session.commit()

    return jsonify({ "message":"Пользователь {} заблокирован".format(user.login)})



@api.route('activate_user', methods=['PUT'])
@login_required
@permission_required(Permission.ADMIN)
def activate_user():
    if not request.is_json:
        return bad_request("No JSON data")
    user_id = request.json["user_id"]

    user = User.query.get_or_404(user_id)
    user.is_active = True
    db.session.add(user)
    db.session.commit()

    return jsonify({ "message":"Пользователь {} разблокирован".format(user.login)})


@api.route('users/<int:id>', methods=['PUT'])
@login_required
@permission_required(Permission.ADMIN)
def update_user(id):

    if not request.is_json:
        return bad_request("No JSON data")

    user = User.query.get_or_404(id)

    login = request.json["login"]
    if login is None or login == "":
        return bad_request("Логин не указан")

    if User.query.filter(User.login == login, User.id != id).first() is not None:
        return bad_request("Пользователь с таким именем уже существует")

    user.login = login

    username = request.json["username"]

    if username is None or username == "":
        return bad_request("Имя пользователя не указано")

    user.username = username

    password = request.json["password"]

    if password is not  None and password != "":
        user.reset_password(id, password)

    db.session.add(user)
    db.session.commit()

    return jsonify({ "message":"Профиль пользователя {} изменени.".format(user.id)})


@api.route('users', methods=['DELETE'])
@login_required
@permission_required(Permission.ADMIN)
def delete_user():
    if not request.is_json:
        return bad_request("No JSON data")
    user_id = request.json["user_id"]

    user = User.query.get_or_404(user_id)

    if user.role.name == "Administrator":
        return bad_request("Администратора удалить нельзя.")

    db.session.delete(user)
    db.session.commit()

    return jsonify({ "message":"Пользователь {} удален".format(user.login)})


