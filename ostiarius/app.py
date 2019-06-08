from sanic import Sanic
from sanic_jwt_extended import JWTManager

from ostiarius.gateway import bp


def create_app() -> Sanic:
    _app = Sanic("ostiarius")

    _app.config['JWT_SECRET_KEY'] = "Chanel's secret key required"
    JWTManager(_app)

    _app.blueprint(bp)

    return _app
