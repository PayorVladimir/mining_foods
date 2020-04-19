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


#добавление клиента в базу
@api.route("service/add_client", methods=["POST"])
def service_create_client():
    if not request.is_json :
        return bad_request("No JSON data")

    token = request.args.get("token")

    if token == "" or token is None:
        return bad_request("Для доступа к этому методу необходимо предоставить токен. Для получения токена обратитесь к администратору.")

    if Setting.query.filter(Setting.value == token).first() is None:
        return bad_request("Неверный токен")

    client = Client.from_json(request.json)
    db.session.add(client)
    db.session.commit()

    return jsonify({"message": "Клиент {} успешно добавлен в базу.".format(client.name) })



@api.route("service/block_client", methods=["PATCH"])
def service_block_client():
    if not request.is_json:
        return bad_request("No JSON data")

    token = request.args.get("token")

    if token == "" or token is None:
        return bad_request(
            "Для доступа к этому методу необходимо предоставить токен. Для получения токена обратитесь к администратору.")

    if Setting.query.filter(Setting.value == token).first() is None:
        return bad_request("Неверный токен")

    card_id = request.json["card_id"]
    client = Client.query.filter(Client.card_id == card_id).first()

    if client is None:
        return bad_request("Клиент с таким пропуском не найден")

    client.is_active = False
    db.session.add(client)
    db.session.commit()
    return jsonify({"message": "Клиент {} заблокирован   .".format(client.name)})

@api.route("service/activate_client", methods=["PATCH"])
def service_activate_client():
    if not request.is_json:
        return bad_request("No JSON data")

    token = request.args.get("token")

    if token == "" or token is None:
        return bad_request(
            "Для доступа к этому методу необходимо предоставить токен. Для получения токена обратитесь к администратору.")

    if Setting.query.filter(Setting.value == token).first() is None:
        return bad_request("Неверный токен")

    card_id = request.json["card_id"]
    client = Client.query.filter(Client.card_id==card_id).first()

    if client is None:
        return bad_request("Клиент с таким пропуском не найден")


    client.is_active = True
    db.session.add(client)
    db.session.commit()
    return jsonify({"message": "Клиент {} заблокирован   .".format(client.name)})



@api.route("service/client/<int:card_id>/", methods=["PUT"])
def service_edit_client(card_id):
    if not request.is_json:
        return bad_request("No JSON data")

    token = request.args.get("token")

    if token == "" or token is None:
        return bad_request(
            "Для доступа к этому методу необходимо предоставить токен. Для получения токена обратитесь к администратору.")

    if Setting.query.filter(Setting.value == token).first() is None:
        return bad_request("Неверный токен")

    client = Client.query.filter(Client.card_id == card_id).first()

    if client is None:
        return bad_request("Клиент с таким пропуском не найден")

    client_name = request.json["client_name"]

    if len(client_name) > 128:
        return bad_request("Имя клиента не должно превышать 128 символов.")

    if Client.query.filter(Client.name == client_name, Client.id != id).first() is not None:
        return bad_request("Клиент с таким именем уже существует")

    if client_name is not None and client_name != "":
        client.name = client_name


    new_card_id = request.json["card_id"]

    if Client.query.filter(Client.card_id == new_card_id, Client.id != id).first() is not None:
        return bad_request("Клиент с таким ID пропуска уже существует")

    if new_card_id is not None and new_card_id != "":
        client.card_id = new_card_id

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



#добавление группы в базу
@api.route('service/add_group', methods=['POST'])

@permission_required(Permission.MODERATE)
def service_new_group():
    if not request.is_json:
        return bad_request("No JSON data")

    token = request.args.get("token")

    if token == "" or token is None:
        return bad_request("Для доступа к этому методу необходимо предоставить токен. Для получения токена обратитесь к администратору.")

    if Setting.query.filter(Setting.value == token).first() is None:
        return bad_request("Неверный токен")

    title = request.json["group_title"]
    if title is None or title == "":
        return bad_request("Название группы не указано")
    if Clientgroup.query.filter(Clientgroup.title == title).first() is not None:
        return bad_request("Группа с таким названием уже существует")

    valid_thru = datetime.datetime.now()

    if valid_thru is None or valid_thru == "":
        return bad_request("Дата блокировки группы не указана")

    user = Clientgroup(is_active=True, title=title, valid_thru=valid_thru)

    db.session.add(user)
    db.session.commit()
    return jsonify({"message": "Группа успешно создана"})


#блокировка группы
@api.route('service/block_group', methods=['PUT'])
def service_block_group():
    if not request.is_json:
        return bad_request("No JSON data")

    token = request.args.get("token")

    if token == "" or token is None:
        return bad_request(
            "Для доступа к этому методу необходимо предоставить токен. Для получения токена обратитесь к администратору.")

    if Setting.query.filter(Setting.value == token).first() is None:
        return bad_request("Неверный токен")
    group_id = request.json["group_id"]

    group = Clientgroup.query.get_or_404(group_id)
    group.is_active = False

    db.session.add(group)
    db.session.commit()

    return jsonify({ "message":"Группа {} заблокирована".format(group.title)})

#активация группы
@api.route('service/activate_group', methods=['PUT'])
def service_activate_group():
    if not request.is_json:
        return bad_request("No JSON data")

    token = request.args.get("token")

    if token == "" or token is None:
        return bad_request(
            "Для доступа к этому методу необходимо предоставить токен. Для получения токена обратитесь к администратору.")

    if Setting.query.filter(Setting.value == token).first() is None:
        return bad_request("Неверный токен")

    group_id = request.json["group_id"]

    group = Clientgroup.query.get_or_404(group_id)
    group.is_active = True
    db.session.add(group)
    db.session.commit()

    return jsonify({ "message":"Группа {} разблокирована".format(group.title)})



@api.route('service/terminal_stats/', methods=['GET'])
def get_terminal_stats():
    if not request.is_json:
        return bad_request("No JSON data")

    token = request.args.get("token")
    uid = request.args.get("uid")


    if Setting.query.filter(Setting.value == token).first() is None:
        return bad_request("Неверный токен")


    if uid == "" or uid is None:
        return bad_request(
            "Не указан идентификатор терминала.")

    if token == "" or token is None:
        return bad_request(
            "Для доступа к этому методу необходимо предоставить токен. Для получения токена обратитесь к администратору.")

    terminal = Terminal.query.filter(Terminal.uid == uid).first()
    if terminal is None or terminal == "":
        return bad_request("Терминал не найден")


    return  jsonify({ "terminal_total_requests": Log.query.filter(cast(Log.time_stamp, Date) == date.today()).count(),
                      "terminal_today_requests": Log.query.filter(Log.terminal_id == terminal.id).filter(cast(Log.time_stamp, Date) == date.today()).count()})
