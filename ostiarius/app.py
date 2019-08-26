import os
import uuid

from entry_logger_sanic import set_logger
from sanic import Sanic
from sanic.exceptions import SanicException
from sanic.response import text, json
from sanic_jwt_extended import JWTManager
from sanic_cors import CORS

from ostiarius.gateway import bp
from ostiarius.vault import settings
from ostiarius.exceptions import ServiceUnavailable


def create_app() -> Sanic:
    _app = Sanic("ostiarius")

    log_path = os.path.dirname(__file__).replace("/ostiarius", "")
    set_logger(_app, log_path)

    _app.config['JWT_SECRET_KEY'] = settings.jwt_secret_key
    _app.config['RBAC_ENABLE'] = True

    JWTManager(_app)
    CORS(_app, automatic_options=True)

    @_app.get('/ping')
    async def ping(request):
        return text("pong")

    @_app.middleware('request')
    async def add_tracking_id(request):
        request.headers.update({"X-Tracking-ID": uuid.uuid4().hex})

    _app.error_handler.add(ServiceUnavailable, lambda r, e: json(body={"msg": "Service unavailable"}, status=503))
    _app.error_handler.add(SanicException, lambda r, e: json(body={"msg": e.args[0]}, status=e.status_code))

    _app.blueprint(bp)

    return _app
