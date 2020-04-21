from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
from flask import request
from config import config
from flask_jsglue import JSGlue
from flask_reverse_proxy_fix.middleware import ReverseProxyPrefixFix

login_manager = LoginManager()



db = SQLAlchemy()
mail = Mail()

#cors support for frontend server
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    if request.method == 'OPTIONS':
        response.headers['Access-Control-Allow-Methods'] = 'DELETE, GET, POST, PUT'
        headers = request.headers.get('Access-Control-Request-Headers')
        if headers:
            response.headers['Access-Control-Allow-Headers'] = headers
    return response


def create_app(config_name):
    app = Flask(__name__)



    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    # implement CORs support
    jsglue = JSGlue(app)
    app.after_request(add_cors_headers)

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