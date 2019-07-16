from sanic import Sanic
from sanic.response import text
from sanic_jwt_extended import JWTManager
from sanic_cors import CORS

from ostiarius.gateway import bp


def create_app() -> Sanic:
    _app = Sanic("ostiarius")

    _app.config['JWT_SECRET_KEY'] = "Chanel's secret key required"
    _app.config['RBAC_ENABLE'] = True

    JWTManager(_app)
    CORS(_app, automatic_options=True)

    @_app.get('/ping')
    async def ping(request):
        return text("pong")

    _app.blueprint(bp)

    return _app
