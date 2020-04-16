from flask import jsonify, request, g, Response
from .. import db
from . import api
from ..models import Terminal, Log, Client, Permission
from .errors import forbidden, bad_request, not_found
import datetime
from datetime import date
from flask_login import current_user, login_user, logout_user, login_required
from .decorators import permission_required
from sqlalchemy import or_, Date, cast


@api.route('clients/get_quote', methods=['GET'])
def get_quote():
    #Check terminal
    terminal_token = request.args.get("token")
    terminal_uid = request.args.get("uid")
    if terminal_uid is None or terminal_uid == "" or terminal_token is None or terminal_token == "":
        return bad_request("Terminal credentials are not provided")

    terminal = Terminal.query.filter(Terminal.uid == terminal_uid).first()
    #check terminal state
    if terminal is None:
        return not_found("Терминал не зарегистрирован")

    if not terminal.is_active:
        return bad_request("Терминал заблокирован")

    if  terminal.verify_token(terminal_token) == False:
         return bad_request("Неверные регистрационные данные терминала")

    #Get client data by card id
    client_card_id = request.args.get("client_card_id")

    if client_card_id is None or client_card_id == "":
        return bad_request("Код карты клиента не предоставлен")


    client = Client.query.filter(Client.card_id == client_card_id).first()
    # check if user registered
    if client is None:
        return bad_request("Пользователь не зарегистрирован.")
    #check if user is blocked
    if not client.is_active:
        return bad_request("Пользователь заблокирован.")


    #check group limitations
    if client.group is not None:
        if not client.group.is_active:
            return bad_request("Группа в которой состоит пользователь заблокирована.")

    #get all logs in last 24 hours ??



    logs = Log.query.filter(Log.client_id == client.id).filter(cast(Log.time_stamp, Date) == date.today()).order_by(Log.id.desc()).all()

    print([log.to_json() for log  in logs])


    #check if 5 minutes passed from last log in this terminal, if not - approve
    now = datetime.datetime.now()
    if logs is not None and len(logs)>0:
        if now - datetime.timedelta(minutes=5) <= logs[0].time_stamp <= now and logs[0].terminal.uid == terminal_uid:
            return jsonify({
            "approved": True,
            "first_time": False,
            "user_name": client.name,
            "group": client.group.title if client.group is not None else "без группы",
            "logs": [log.to_json() for log in logs],
            "quota": client.quota,
        })


    #if quota limit is reached - disapprove
    if len(logs) >= client.quota:
            return jsonify({
                "approved": False,
                "user_name": client.name,
                "group": client.group.title if client.group is not None else "без группы",
                "logs": [log.to_json() for log in logs],
                "quota": client.quota
            })

    new_log = Log(terminal_id=terminal.id, client_id=client.id, client_group_name= client.group.title if client.group is not None else "без группы",\
                  client_card=client.card_id, terminal_name=terminal.description, client_name=client.name)

    terminal.total_requests += 1

    db.session.add(terminal)
    db.session.add(new_log)
    db.session.commit()

    logs = Log.query.filter(Log.client_id == client.id).filter(cast(Log.time_stamp, Date) == date.today()).all()
    return jsonify({
        "approved": True,
        "first_time": True,
        "user_name": client.name,
        "group": client.group.title if client.group is not None else "без группы",
        "logs": [log.to_json() for log in logs],
        "quota": client.quota
    })


@api.route('clients/', methods=['GET', 'POST'] )
@login_required
@permission_required(Permission.MODERATE)
def get_clients():


    page = request.form["page"]
    rows = request.form["rows"]
    query = None
    if "query" in request.form:
        query = request.form["query"]


    if query is not None and query !="":

        clients =  Client.query.filter(or_(Client.name.like("%{}%".format(query)),(Client.card_id.like("%{}%".format(query))))).paginate(page=int(page), error_out=False, per_page=int(rows)).items
    else:
        clients = Client.query.paginate(page=int(page), error_out=False, per_page=int(rows)).items

    return jsonify({"total":len(Client.query.all()),"rows":[client.to_json() for client in clients]})

@api.route("client", methods=["POST"])
@login_required
@permission_required(Permission.MODERATE)
def create_client():
    if not request.is_json :
        return bad_request("No JSON data")


    client = Client.from_json(request.json)

    db.session.add(client)
    db.session.commit()
    return jsonify({"message": "Клиент {} успешно добавлен в базу.".format(client.name) })


@api.route("client", methods=["DELETE"])
@login_required
@permission_required(Permission.MODERATE)
def delete_client():

    if not request.is_json :

        return bad_request("No JSON data")
    client_id = request.json["client_id"]

    client = Client.query.get_or_404(client_id)
    db.session.delete(client)
    db.session.commit()
    return jsonify({"message": "Клиент {} успешно удален из базы.".format(client.name) })


@api.route("block_client", methods=["PUT"])
@login_required
@permission_required(Permission.MODERATE)
def block_client():
    if not request.is_json:
        return bad_request("No JSON data")

    client_id = request.json["client_id"]

    client = Client.query.get_or_404(client_id)

    client.is_active = False
    db.session.add(client)
    db.session.commit()
    return jsonify({"message": "Клиент {} заблокирован   .".format(client.name)})



@api.route("activate_client", methods=["PUT"])
@login_required
@permission_required(Permission.MODERATE)
def activate_client():
    if not request.is_json:
        return bad_request("No JSON data")
    client_id = request.json["client_id"]
    client = Client.query.get_or_404(client_id)


    client.is_active = True
    db.session.add(client)
    db.session.commit()
    return jsonify({"message": "Клиент {} заблокирован   .".format(client.name)})



@api.route("client/<int:id>/", methods=["PUT"])
@login_required
@permission_required(Permission.MODERATE)
def edit_client(id):
    if not request.is_json:
        return bad_request("No JSON data")

    client = Client.query.get_or_404(id)

    client_name = request.json["client_name"]

    if len(client_name) > 128:
        return bad_request("Имя клиента не должно превышать 128 символов.")

    if Client.query.filter(Client.name == client_name, Client.id != id).first() is not None:
        return bad_request("Клиент с таким именем уже существует")

    if client_name is not None and client_name != "":
        client.name = client_name


    card_id = request.json["card_id"]

    if Client.query.filter(Client.card_id == card_id, Client.id != id).first() is not None:
        return bad_request("Клиент с таким ID пропуска уже существует")

    if card_id is not None and card_id != "":
        client.card_id = card_id

    quota = int(request.json["quota"])

    if quota > 100:
        return bad_request("Квота питания не должна превышать 100 раз в день.")

    if quota is not None and quota != "":
        client.quota = quota

    group_id = request.json["group"]

    if group_id == "" or group_id is None:
        client.group_id = None
    elif group_id.isdigit():
        client.group_id = group_id

    db.session.add(client)
    db.session.commit()
    return jsonify({"message": "Клиент {} успешно обновлен в базе данных.".format(client.name)})
