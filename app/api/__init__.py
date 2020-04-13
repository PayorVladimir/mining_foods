from flask import Blueprint
from ..models import Permission
api = Blueprint('api', __name__)

@api.app_context_processor
def inject_permissions():
    return dict(Permission=Permission)

from . import clients, terminals, logs, users, groups, settings, service
