from functools import wraps
from flask import g
from .errors import forbidden

def permission_required(permission):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not g.user.can(permission):
                return forbidden('Не достаточно прав доступа')
            return f(*args, **kwargs)
        return decorated_function

    return decorator
