from flask import Blueprint
from ..models import Permission
from flask_cors import CORS

api = Blueprint('api', __name__)
CORS(api, resources={r"/*": {"origins": "*"}}, headers='Content-Type', supports_credentials=True)
@api.app_context_processor
def inject_permissions():
    return dict(Permission=Permission)

from . import clients, terminals, logs, users, groups, settings, service
