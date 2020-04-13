from flask import jsonify, request, g, Response
from .. import db
from . import api
from ..models import Setting, Permission
from .errors import forbidden, bad_request, not_found
from flask_login import current_user, login_user, logout_user, login_required
import datetime
from .decorators import permission_required
from sqlalchemy import desc





@api.route('settings/', methods=['GET'] )
@login_required
@permission_required(Permission.ADMIN)
def get_settings():

    settings = Setting.query.all()

    return jsonify({"settings":[setting.to_json() for setting in settings]})

@api.route('settings/<int:id>', methods=['PUT'] )
@login_required
@permission_required(Permission.ADMIN)
def update_setting():

    if not request.is_json:
        return bad_request("No JSON data")

    setting = Setting.query.get_or_404(id)
    new_value = request.json["value"]
    label = request.json["label"]
    if len(label) > 64:
        return bad_request("Название параметра не должно превышать 64 символов.")
    if len(new_value) > 64:
        return bad_request("Значение параметра не должно превышать 64 символов.")

    if Setting.query.filter(Setting.label == label).first() is not None and  label != setting.value:
        return bad_request("Такой параметр уже существует")
    setting.value = new_value
    db.session.add(setting)
    db.session.commit()

    return jsonify({ "message":"Параметр {} изменен.".format(setting.label)})


@api.route('settings/', methods=['POST'] )
@login_required
@permission_required(Permission.ADMIN)
def create_settings():
    if not request.is_json:
        return bad_request("No JSON data")
    value = request.json["value"]
    label = request.json["label"]
    if len(label) > 64:
        return bad_request("Название параметра не должно превышать 64 символов.")
    if len(value) > 64:
        return bad_request("Значение параметра не должно превышать 64 символов.")

    if Setting.query.filter(Setting.label == label).first() is not None:
        return bad_request("Такой параметр уже существует")

    setting = Setting(label=label,value=value)
    db.session.add(setting)
    db.session.commit()

    return jsonify({ "message":"Параметр {} добавлен в базу данных.".format(setting.label)})
