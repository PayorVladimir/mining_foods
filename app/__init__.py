from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
from flask import request
from config import config
from flask_jsglue import JSGlue
from flask_reverse_proxy_fix.middleware import ReverseProxyPrefixFix
import datetime
import time
from flask_cors import CORS

import colors
from flask import g, request
from rfc3339 import rfc3339

login_manager = LoginManager()
from flask_wtf import CsrfProtect

# csrf = CsrfProtect()



db = SQLAlchemy()
mail = Mail()

#cors support for frontend server
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    if request.method == 'OPTIONS':
        response.headers['Access-Control-Allow-Methods'] = 'DELETE, GET, POST, PUT, PATCH'
        headers = request.headers.get('Access-Control-Request-Headers')
        if headers:
            response.headers['Access-Control-Allow-Headers'] = headers
        origin = request.headers.get('Origin', '')
        if origin.endswith('digital.spmi.ru'):
                response.headers['Access-Control-Allow-Origin'] = origin
                response.headers['Access-Control-Allow-Credentials'] = 'true'
    return response


def create_app(config_name):
    app = Flask(__name__)

    CORS(app)

    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    # implement CORs support
    jsglue = JSGlue(app)
    app.after_request(add_cors_headers)

    #csrf.init_app(app)

    @app.before_request
    def start_timer():
        g.start = time.time()

    @app.after_request
    def log_request(response):
        if request.path == '/favicon.ico':
            return response
        elif request.path.startswith('/static'):
            return response

        now = time.time()

        dt = datetime.datetime.fromtimestamp(now)
        timestamp = rfc3339(dt, utc=True)

        ip = request.headers.get('X-Forwarded-For', request.remote_addr)
        host = request.host.split(':', 1)[0]
        args = dict(request.args)

        log_params = [
            ('method', request.method, 'blue'),
            ('path', request.path, 'blue'),
            ('status', response.status_code, 'yellow'),

            ('time', timestamp, 'magenta'),
            ('ip', ip, 'red'),
            ('host', host, 'red'),
            ('params', args, 'blue')
        ]

        request_id = request.headers.get('X-Request-ID')
        if request_id:
            log_params.append(('request_id', request_id, 'yellow'))

        parts = []
        for name, value, color in log_params:
            part = colors.color("{}={}".format(name, value), fg=color)
            parts.append(part)
        line = " ".join(parts)

        app.logger.info(line)

        return response

    db.init_app(app)
    login_manager.init_app(app)
    ReverseProxyPrefixFix(app)
    login_manager.login_view = 'auth.login'

    from .api import api as api_blueprint
    from .main import main as main_blueprint
    from .auth import auth as auth_blueprint

    app.register_blueprint(main_blueprint)
    app.register_blueprint(api_blueprint, url_prefix='/api/v1/')
    app.register_blueprint(auth_blueprint, url_prefix='/auth/')


    return app