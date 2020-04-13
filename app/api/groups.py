from flask import jsonify, request, g, Response
from .. import db
from . import api
from ..models import Clientgroup, Log, Client, Permission
from flask_login import current_user, login_user, logout_user, login_required
from .decorators import permission_required
from .errors import forbidden, bad_request, not_found
import datetime


#initial groups
@api.before_app_first_request
def create_basic_groups():

    students = Clientgroup(title="Студенты", is_active=True, valid_thru= datetime.datetime(2021, 1, 1))
    profsouz = Clientgroup(title="Участники профсоюза", is_active=True, valid_thru= datetime.datetime(2021, 1, 1))


    if Clientgroup.query.filter_by(title= students.title).first() is None:
        db.session.add(students)

    if Clientgroup.query.filter_by(title=profsouz.title).first() is None:
        db.session.add(profsouz)

    db.session.commit()

@api.route('new_group', methods=['POST'])
@login_required
@permission_required(Permission.MODERATE)
def new_group():
    if not request.is_json:
        return bad_request("No JSON data")

    title = request.json["group_title"]
    if title is None or title == "":
        return bad_request("Название группы не указано")
    if Clientgroup.query.filter(Clientgroup.title == title).first() is not None:
        return bad_request("Группа с таким названием уже существует")
    # valid_thru = request.json["valid_thru"]
    # print(valid_thru)
    # valid_thru  =  datetime.datetime.strptime(valid_thru, '%m/%d/%Y %H:%M')

    valid_thru = datetime.datetime.now()

    if valid_thru is None or valid_thru == "":
        return bad_request("Дата блокировки группы не указана")


    user = Clientgroup(is_active=True, title=title, valid_thru=valid_thru)



    db.session.add(user)
    db.session.commit()
    return jsonify({"message": "Группа успешно создана"})




@api.route('groups_all/', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.MODERATE)
def get_all_groups():
    groups = Clientgroup.query.all()
    groups_json=[group.to_json() for group in groups]
    groups_json.append({"group_title": "без группы", "group_id": ""})
    return jsonify(groups_json)

@api.route('groups/', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.MODERATE)
def get_groups():

    page = request.form["page"]
    rows = request.form["rows"]

    groups = Clientgroup.query.paginate(page=int(page), error_out=False, per_page=int(rows)).items
    return jsonify({
        "total":len(groups),
        "rows": [group.to_json() for group in groups]
         })


@api.route('block_group', methods=['PUT'])
@login_required
@permission_required(Permission.MODERATE)
def block_group():
    if not request.is_json:
        return bad_request("No JSON data")
    group_id = request.json["group_id"]

    group = Clientgroup.query.get_or_404(group_id)
    group.is_active = False

    db.session.add(group)
    db.session.commit()

    return jsonify({ "message":"Группа {} заблокирована".format(group.title)})



@api.route('activate_group', methods=['PUT'])
@login_required
@permission_required(Permission.MODERATE)
def activate_group():
    if not request.is_json:
        return bad_request("No JSON data")
    group_id = request.json["group_id"]

    group = Clientgroup.query.get_or_404(group_id)
    group.is_active = True
    db.session.add(group)
    db.session.commit()

    return jsonify({ "message":"Группа {} разблокирована".format(group.title)})


@api.route('groups/<int:id>', methods=['PUT'])
@login_required
@permission_required(Permission.MODERATE)
def update_group(id):
    if not request.is_json:
        return bad_request("No JSON data")
    group_title = request.json["group_title"]

    if len(group_title) > 128:
        return bad_request("Название группы не должно превышать 128 символов")

    if group_title == "" or group_title is None:
        return bad_request("Не указано название группы")

    # group_valid_thru = request.json["valid_thru"]
    group_valid_thru = datetime.datetime.now()
    if group_valid_thru == "" or group_valid_thru is None:
        return bad_request("Не указана дата блокировки группы")

    if Clientgroup.query.filter(Clientgroup.title == group_title).first() is not\
            None and Clientgroup.query.get(id).title != group_title:
        return bad_request("Группа с таким названием уже существует")


    group = Clientgroup.query.get_or_404(id)

    group.title = group_title

    group.valid_thru = group_valid_thru


    db.session.add(group)
    db.session.commit()

    return jsonify({ "message":"Профиль группы {} изменен.".format(group.title)})



@api.route('delete_group', methods=['DELETE'])
@login_required
@permission_required(Permission.MODERATE)
def delete_group():
    if not request.is_json:
        return bad_request("No JSON data")
    group_id = request.json["group_id"]

    group = Clientgroup.query.get_or_404(group_id)
    db.session.delete(group)
    db.session.commit()

    return jsonify({ "message":"Группа {} удалена.".format(group.title)})
