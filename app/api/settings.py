from flask import jsonify, request, g, Response, make_response
from .. import db
from . import api
from ..models import Setting, Permission
from .errors import forbidden, bad_request, not_found
from flask_login import current_user, login_user, logout_user, login_required
import datetime
from .decorators import permission_required
from sqlalchemy import desc
import secrets

@api.route('settings/', methods=['GET'] )
@login_required
@permission_required(Permission.ADMIN)
def get_settings():

    settings = Setting.query.filter(Setting.label!="pin")

    return jsonify({"settings":[setting.to_json() for setting in settings]})


@api.route('settings/update_pin', methods=['PATCH'] )
@login_required
@permission_required(Permission.ADMIN)
def update_pin():
    if not request.is_json:
        return bad_request("No JSON data")


    pin = request.json["pin"]
    print(pin)
    if len(pin) > 4:
        return bad_request("Название параметра не должно превышать 4 цифры.")


    pin_code = Setting.query.filter(Setting.label == "pin").first()

    if pin_code is None:
        return bad_request("Не удалось выполнить запрос. Пин-код не инициализирован в базе данных.")
    pin_code.value = pin


    db.session.add(pin_code)
    db.session.commit()

    return jsonify({"message": "ПИН-код терминалов изменен."})


@api.route('settings/<int:id>', methods=['PUT'] )
@login_required
@permission_required(Permission.ADMIN)
def update_setting(id):

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


@api.route('settings/<string:value>', methods=['DELETE'] )
@login_required
@permission_required(Permission.ADMIN)
def delete_setting(value):



    setting = Setting.query.filter(Setting.value==value, Setting.label != "pin").first()
    if setting is None:
        return not_found("Токен не найден")


    db.session.delete(setting)
    db.session.commit()

    return jsonify({ "message":"Настройка {} удалена".format(id)})


@api.route('settings/', methods=['POST'] )
@login_required
@permission_required(Permission.ADMIN)
def create_settings():


    if not request.is_json:
        return bad_request("No JSON data")

    label = request.json["label"]
    if len(label) > 64:
        return bad_request("Название токена не должно превышать 64 символов.")

    if Setting.query.filter(Setting.label == label).first() is not None:
        return bad_request("Такой параметр уже существует")

    setting = Setting(label=label,value=secrets.token_urlsafe(16))
    db.session.add(setting)
    db.session.commit()

    return jsonify({ "message":"Параметр {} добавлен в базу данных.".format(setting.label)})


