import os
import sys
from datetime import datetime, timedelta, date
from flask_login import UserMixin, AnonymousUserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from flask import current_app, g
from app.exceptions import ValidationError
from . import db, login_manager
from sqlalchemy import event
from sqlalchemy import or_, Date, cast

topdir = os.path.join(os.path.dirname(__file__), "")
sys.path.append(topdir)


class Permission:
    VIEW = 1
    CREATE = 2
    MODERATE = 8
    ADMIN = 16


class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)
    users = db.relationship('User', backref='role', lazy='dynamic')

    def __init__(self, **kwargs):
        super(Role, self).__init__(**kwargs)
        if self.permissions is None:
            self.permissions = 0

    def add_permission(self, perm):
        if not self.has_permission(perm):
            self.permissions += perm

    def remove_permission(self, perm):
        if self.has_permission(perm):
            self.permissions -= perm

    def reset_permissions(self):
        self.permissions = 0

    def has_permission(self, perm):
        return self.permissions & perm == perm

    def to_json(self):
        json_role = {
            "label": self.name,
            "id": self.id,
        }
        return json_role

    def __repr__(self):
        return '<Role %r>' % self.name


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    login = db.Column(db.String(64), unique=True, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'))
    is_active = db.Column(db.BOOLEAN, default=True)
    password_hash = db.Column(db.String(128))
    registered = db.Column(db.DateTime(), default=datetime.utcnow)

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role is None:
            if self.login == current_app.config['SYSTEM_ADMIN']:
                self.role = Role.query.filter_by(name='Administrator').first()
            if self.role is None:
                self.role = Role.query.filter_by(default=True).first()

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
         password = check_password_hash(self.password_hash, password)

         return password and self.is_active

    @staticmethod
    def reset_password(id, new_password):
        user = User.query.get_or_404(id)
        user.password = new_password
        db.session.add(user)
        return True

    def can(self, perm):
        return self.role is not None and self.role.has_permission(perm)

    def is_administrator(self):
        return self.can(Permission.ADMIN)

    def ping(self):
        self.last_seen = datetime.utcnow
        db.session.add(self)


    def to_json(self):
        json_user = {
            'user_id': self.id,
            'user_login': self.login,
            'user_name': self.username,
            'user_registered': self.registered.strftime("%m/%d/%Y, %H:%M:%S"),
            'user_role': self.role.name,
            'is_active': "активен" if self.is_active else "заблокирован",

        }
        return json_user

    def __repr__(self):
        return '<User %r>' % self.username


class AnonymousUser(AnonymousUserMixin):
    def can(self, permissions):
        return False

    def is_administrator(self):
        return False
login_manager.anonymous_user = AnonymousUser


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class Client(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True)
    card_id = db.Column(db.String(64), unique=True, index=True)
    quota = db.Column(db.SMALLINT, default=1)
    is_active = db.Column(db.BOOLEAN, default=True)
    registered = db.Column(db.DateTime(), default=datetime.now)
    valid_thru = db.Column(db.DateTime())
    group_id = db.Column(db.Integer, db.ForeignKey('clientgroup.id'))

    logs = db.relationship('Log', backref='client', lazy='dynamic')

    def from_json(json_client):
        client_name = json_client["client_name"]
        card_id = json_client["card_id"]
        group = json_client["group"]
        quota = json_client["quota"]

        if card_id is None or card_id == "":
            raise ValidationError("Не указан ID пропуска")

        if client_name is None or client_name == "":
            raise ValidationError("Не указано имя клиента")


        if quota is None or quota == "":
            quota = 1


        if group == "":
            group = None

        if Client.query.filter(Client.name == client_name).first() is not None:
            raise ValidationError("Клиент с таким именем уже существует")

        if Client.query.filter(Client.card_id == card_id).first() is not None:
            raise ValidationError("Клиент с таким номером пропуска уже существует")

        return Client(name=client_name, card_id=card_id, quota=quota, group_id=group)

    def to_json(self) :
        is_active = "активен"
        if not  self.is_active:
            is_active = "заблокирован"
        if self.group is not None and not self.group.is_active:
            is_active = "заблокирован по группе"

        client_json = {
            "client_id": self.id,
            "client_name": self.name,
            "card_id": self.card_id,
            "quota": self.quota,
            "group": self.group.title if  self.group is not None  else "без группы" ,
            "is_active": is_active,
        }
        return client_json

class Clientgroup(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128), unique=True, index=True)
    valid_thru = db.Column(db.DateTime())
    is_active = db.Column(db.BOOLEAN, default=True)
    clients = db.relationship('Client', backref='group', lazy='dynamic')

    def to_json(self):
        json_group = {
            "group_id": self.id,
            "group_title": self.title,
            "total_clients": self.clients.count(),
            "valid_thru": self.valid_thru.strftime("%m/%d/%Y, %H:%M:%S"),
            "is_active": "активна" if self.is_active else "заблокирована",
        }

        return json_group

class Terminal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    total_requests = db.Column(db.Integer, default=0)
    uid = db.Column(db.String(128), unique=True, index=True)
    description = db.Column(db.String(128), index=True)
    registered = db.Column(db.DateTime(), default=datetime.now)
    token_hash = db.Column(db.String(128))
    is_active = db.Column(db.BOOLEAN, default=True)


    logs = db.relationship('Log', backref='terminal', lazy='dynamic')

    def __init__(self, **kwargs):
        super(Terminal, self).__init__(**kwargs)


    @property
    def token(self):
        raise AttributeError('token is not a readable attribute')

    @token.setter
    def token(self, token):
        self.token_hash = generate_password_hash(token)

    def verify_token(self, token):
        return check_password_hash(self.token_hash, token)


    def to_json(self):

        requests_per_day = Log.query.filter(Log.terminal_id == self.id).filter(cast(Log.time_stamp, Date) == date.today()).count()
        json_terminal = {
            "terminal_id": self.id,
            "terminal_description": self.description,
            "terminal_uid": self.uid,
            "total_requests": self.total_requests,
            "requests_per_day": requests_per_day,
            "date_registred": self.registered.strftime("%m/%d/%Y, %H:%M:%S"),
            "is_active": "активен" if self.is_active else "заблокирован",

        }

        return json_terminal

class Log(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    time_stamp = db.Column(db.DateTime(), default=datetime.now)
    terminal_id =  db.Column(db.Integer, db.ForeignKey('terminal.id'))
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'))
    terminal_name =  db.Column(db.String(128))
    client_name =  db.Column(db.String(128))
    client_card =  db.Column(db.Integer)
    client_group_name = db.Column(db.String(128))


    def to_json(self):
        json_log = {
            "log_id": self.id,
            "time_stamp": self.time_stamp.strftime("%m/%d/%Y, %H:%M:%S"),
            "terminal_name": self.terminal_name,
            "client_name": self.client_name,
            "client_card": self.client_card,
            "client_group_name": self.client_group_name,
            "client_id": self.client_id if self.client_id is not None else "удален",

        }
        return json_log


class Setting(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    label = db.Column(db.String(64), unique=True, index=True)
    value = db.Column(db.String(64), unique=True, index=True)

    def to_json(self):
        json_setting = {
            "label": self.label,
            "value": self.value
        }
        return json_setting