from flask import jsonify, request, g, Response
from .. import db
from . import api
from ..models import Terminal, Log, Client, Permission, Setting
from .errors import forbidden, bad_request, not_found
from flask_login import current_user, login_user, logout_user, login_required
from .decorators import permission_required
import secrets


#initial terminal pin
@api.before_app_first_request
def create_terminal_pincode():

    pincode = Setting(label="pin", value="1773")

    if Setting.query.filter_by(label= pincode.label).first() is None:
        db.session.add(pincode)

    db.session.commit()

@api.route('terminals/', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.MODERATE)
def get_terminals():

    page = request.form["page"]
    rows = request.form["rows"]

    terminals = Terminal.query.paginate(page=int(page), error_out=False, per_page=int(rows)).items
    return jsonify({
        "total":len(terminals),
        "rows": [terminal.to_json() for terminal in terminals]
                   })


@api.route('block_terminal', methods=['PUT'])
@login_required
@permission_required(Permission.ADMIN)
def block_terminal():
    if not request.is_json:
        return bad_request("No JSON data")
    terminal_id = request.json["terminal_id"]

    terminal = Terminal.query.get_or_404(terminal_id)
    terminal.is_active = False

    db.session.add(terminal)
    db.session.commit()

    return jsonify({ "message":"Терминал {} заблокирован".format(terminal.uid)})


@api.route('activate_terminal', methods=['PUT'])
@login_required
@permission_required(Permission.ADMIN)
def activate_terminal():
    if not request.is_json:
        return bad_request("No JSON data")
    terminal_id = request.json["terminal_id"]

    terminal = Terminal.query.get_or_404(terminal_id)
    terminal.is_active = True
    db.session.add(terminal)
    db.session.commit()

    return jsonify({ "message":"Терминал {} активирован".format(terminal.uid)})


@api.route('terminals/<int:id>', methods=['PUT'])
@login_required
@permission_required(Permission.MODERATE)
def update_terminal(id):
    if not request.is_json:
        return bad_request("No JSON data")
    terminal_description = request.json["terminal_description"]

    if len(terminal_description) >128:
        return bad_request("Название терминала не должно превышать 128 символов.")


    terminal = Terminal.query.get_or_404(id)
    terminal.description = terminal_description

    db.session.add(terminal)
    db.session.commit()

    return jsonify({ "message":"Терминал {} переименован.".format(terminal.uid)})


@api.route('delete_terminal', methods=['DELETE'])
@login_required
@permission_required(Permission.ADMIN)
def delete_terminal():
    if not request.is_json:
        return bad_request("No JSON data")
    terminal_id = request.json["terminal_id"]

    terminal = Terminal.query.get_or_404(terminal_id)
    db.session.delete(terminal)
    db.session.commit()

    return jsonify({ "message":"Терминал {} удален".format(terminal.uid)})


@api.route('terminal/register/', methods=['GET'])
def register_terminal():
    terminal_uid = request.args.get("uid")


    if terminal_uid is None or terminal_uid == "":
        return bad_request("No UID provided")

    same_terminal = Terminal.query.filter(Terminal.uid == terminal_uid).first()

    if same_terminal is not None:
        return bad_request("Terminal with this UID is already registered")


    token = secrets.token_urlsafe(32)
    last_terminal = Terminal.query.order_by(Terminal.id.desc()).first()
    terminal_id = str(last_terminal.id + 1) if last_terminal is not None else "1"

    new_terminal = Terminal(uid=terminal_uid, token=token, description="Terminal-"+terminal_id)
    db.session.add(new_terminal)
    db.session.commit()

    terminal = Terminal.query.filter(Terminal.uid == terminal_uid).first()

    return jsonify({'token' : token, 'id': terminal.id })


@api.route('terminal/login/', methods=['GET'])
def pincode_terminal():
    pincode = request.args.get("pin")



    if Setting.query.filter(Setting.label== "pin", Setting.value==str(pincode)).first() is None:

        return jsonify({'approved': False, 'message': "Введен неверный PIN"})



    return jsonify({'approved' : True, 'message':"Доступ разрешен"})


@api.route('terminal/status/', methods=['GET'])
def status_terminal():
    terminal_uid = request.args.get("uid")
    terminal  = Terminal.query.filter(Terminal.uid == terminal_uid).first()

    if terminal is None:
        return jsonify({'status': "unregistered"})

    if not terminal.is_active:
        return jsonify({'status': "banned"})

    return jsonify({'status': "active"})