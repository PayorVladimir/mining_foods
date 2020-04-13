from flask import jsonify, request, g, Response
from .. import db
from . import api
from ..models import Terminal, Log, Client, Permission, Setting
from .errors import forbidden, bad_request, not_found
import datetime
from flask_login import current_user, login_user, logout_user, login_required
from .decorators import permission_required

@api.before_app_first_request
def create_app_token():

    pincode = Setting(label="service_token", value="OXsqAi0OXEWtZK9-ygwMdv7lgChBAz5stqUfUioVVE8")

    if Setting.query.filter_by(label= pincode.label).first() is None:
        db.session.add(pincode)

    db.session.commit()

@api.route("service/add_client", methods=["POST"])

def service_create_client():
    if not request.is_json :
        return bad_request("No JSON data")

    token = request.args.get("token")

    if token == "" or token is None:
        return bad_request("No token")

    if Setting.query.filter(Setting.value == token, Setting.label == "service_token").first() is None:
        return bad_request("Wrong token")

    client = Client.from_json(request.json)
    db.session.add(client)
    db.session.commit()

    return jsonify({"message": "Клиент {} успешно добавлен в базу.".format(client.name) })
