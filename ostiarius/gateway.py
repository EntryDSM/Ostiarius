import requests
from requests import Response
from sanic import Blueprint
from sanic.request import Request
from sanic.response import json
from sanic_jwt_extended.tokens import Token
from requests.exceptions import ConnectionError

from ostiarius.authorizer import auth
from ostiarius.const import ROOT_ADMIN, HERMES, SERVICE, ADMIN, APPLICANT

bp = Blueprint("user", url_prefix="/api/v1")


def trans_request(request: Request, host: str, url: str = None):
    try:
        r: Response = getattr(requests, request.method.lower())(
            url=host+url if url else host+request.path,
            data=None if request.method == "GET" else request.json,
            headers=request.headers,
            params=request.args,
        )
    except ConnectionError:
        return json(
            body={"msg": "Service unavailable"},
            status=503
        )

    if r.status_code / 100 == 5:
        return json(
            body={"msg": "Service unavailable"},
            status=503
        )

    return json(
        body=r.json(),
        headers=r.headers,
        status=r.status_code,
    )


@bp.post('/admin')
@auth(eligible_authority=[ROOT_ADMIN, ])
async def admin_post(request: Request, token: Token, *args, **kwargs):
    return trans_request(request, HERMES)


@bp.get('/admin/batch')
@auth(eligible_authority=[ROOT_ADMIN, SERVICE, ])
async def admin_batch_get(request: Request, token: Token, *args, **kwargs):
    return trans_request(request, HERMES)


@bp.patch('/admin/<admin_id>')
@auth(eligible_authority=[ROOT_ADMIN, SERVICE, ])
async def admin_admin_id_patch(request: Request, token: Token, admin_id: str, *args, **kwargs):
    return trans_request(request, HERMES)


@bp.delete('/admin/<admin_id>')
@auth(eligible_authority=[ROOT_ADMIN, SERVICE, ])
async def admin_admin_id_delete(request: Request, token: Token, admin_id: str, *args, **kwargs):
    return trans_request(request, HERMES)


@bp.get('/admin/<admin_id>')
@auth(eligible_authority=[ROOT_ADMIN, SERVICE, ])
async def admin_admin_id_get(request: Request, token: Token, admin_id: str, *args, **kwargs):
    return trans_request(request, HERMES)


@bp.get('/admin/me')
@auth(eligible_authority=[ADMIN, ROOT_ADMIN, ])
async def admin_admin_id_get(request: Request, token: Token, *args, **kwargs):
    return trans_request(request, HERMES, f"/admin/{token.jwt_identity}")


@bp.post('/applicant')
@auth(eligible_authority=[SERVICE, ])
async def applicant_post(request: Request, token: Token, *args, **kwargs):
    return trans_request(request, HERMES)


@bp.get('/applicant/batch')
@auth(eligible_authority=[ROOT_ADMIN, ])
async def applicant_batch_get(request: Request, token: Token, *args, **kwargs):
    return trans_request(request, HERMES)


@bp.patch('/applicant/<email>')
@auth(eligible_authority=[SERVICE, ])
async def applicant_email_patch(request: Request, token: Token, email: str, *args, **kwargs):
    return trans_request(request, HERMES)


@bp.delete('/applicant/<email>')
@auth(eligible_authority=[ADMIN, ROOT_ADMIN, SERVICE, ])
async def applicant_email_patch(request: Request, token: Token, email: str, *args, **kwargs):
    return trans_request(request, HERMES)


@bp.get('/applicant/me')
@auth(eligible_authority=[APPLICANT, ])
async def applicant_me_get(request: Request, token: Token, email: str, *args, **kwargs):
    return trans_request(request, HERMES, f"/applicant/{token.jwt_identity}")


@bp.patch('/applicant/me')
@auth(eligible_authority=[APPLICANT, ])
async def applicant_me_patch(request: Request, token: Token, email: str, *args, **kwargs):
    return trans_request(request, HERMES, f"/applicant/{token.jwt_identity}")


@bp.put('/applicant/me/photo')
@auth(eligible_authority=[APPLICANT, ])
async def applicant_me_photo_put(request: Request, token: Token, email: str, *args, **kwargs):
    pass
