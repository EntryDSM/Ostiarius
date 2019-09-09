import asyncio
import os
import time
import uuid

import requests
from requests import Response
from sanic import Blueprint
from sanic.request import Request
from sanic.response import json, HTTPResponse, file
from sanic_jwt_extended import create_access_token, create_refresh_token, jwt_required
from sanic_jwt_extended.tokens import Token
from requests.exceptions import ConnectionError

import aiofiles

from ostiarius.const import ROOT_ADMIN, HERMES, ADMIN, APPLICANT, UPLOAD_DIR, LV
from ostiarius.exceptions import ServiceUnavailable

bp = Blueprint("user", url_prefix="/api/v1")


def trans_request(request: Request, host: str, url: str = None, token: Token = None, retry: int = 3):
    headers = request.headers

    if token:
        headers.update({
            "X-User-Type": token.raw_jwt["role"],
            "X-User-Identity": token.raw_jwt["identity"]
        })

    try:
        r: Response = getattr(requests, request.method.lower())(
            url=host + url if url else host + request.path,
            json=None if request.method == "GET" else request.json,
            headers=headers,
            params=request.args,
            timeout=5
        )
    except ConnectionError:
        raise ServiceUnavailable

    if r.status_code / 100 == 5:
        raise ServiceUnavailable

    return json(
        body=r.json(),
        headers=r.headers,
        status=r.status_code,
    )


"""
Temp Login
"""


@bp.post('/applicant/login')
async def login(request: Request):
    email = request.json.get('email', None)
    password = request.json.get('password', None)

    access_token = await create_access_token(identity=email, role=APPLICANT, app=request.app)
    refresh_token = await create_refresh_token(identity=email, app=request.app)

    return json(dict(
        access=access_token,
        refresh=refresh_token
    ), status=201)


@bp.post('/admin/login')
async def login(request: Request):
    email = request.json.get('email', None)
    password = request.json.get('password', None)

    access_token = await create_access_token(identity=email, role=ROOT_ADMIN, app=request.app)
    refresh_token = await create_refresh_token(identity=email, app=request.app)

    return json(dict(
        access=access_token,
        refresh=refresh_token
    ), status=201)


"""
Hermes Routing
"""


@bp.post('/admin')
@jwt_required(allow=[ROOT_ADMIN, ])
async def admin_post(request: Request, token: Token, *args, **kwargs):
    return trans_request(request, HERMES, token=token)


@bp.get('/admin/batch')
@jwt_required(allow=[ROOT_ADMIN, ])
async def admin_batch_get(request: Request, token: Token, *args, **kwargs):
    return trans_request(request, HERMES, token=token)


@bp.patch('/admin/<admin_id>')
@jwt_required(allow=[ROOT_ADMIN, ])
async def admin_admin_id_patch(request: Request, token: Token, admin_id: str, *args, **kwargs):
    return trans_request(request, HERMES, token=token)


@bp.delete('/admin/<admin_id>')
@jwt_required(allow=[ROOT_ADMIN, ])
async def admin_admin_id_delete(request: Request, token: Token, admin_id: str, *args, **kwargs):
    return trans_request(request, HERMES, token=token)


@bp.get('/admin/<admin_id>')
@jwt_required(allow=[ROOT_ADMIN, ])
async def admin_admin_id_get(request: Request, token: Token, admin_id: str, *args, **kwargs):
    return trans_request(request, HERMES, token=token)


@bp.patch('/admin/me')
@jwt_required(allow=[ROOT_ADMIN, ADMIN, ])
async def admin_admin_id_get(request: Request, token: Token, *args, **kwargs):
    return trans_request(request, HERMES, f"/admin/{token.jwt_identity}", token=token)


@bp.post('/applicant')
@jwt_required(allow=[ROOT_ADMIN, ADMIN, ])
async def applicant_post(request: Request, token: Token, *args, **kwargs):
    return trans_request(request, HERMES, token=token)


@bp.get('/applicant/batch')
@jwt_required(allow=[ROOT_ADMIN, ADMIN, ])
async def applicant_batch_get(request: Request, token: Token, *args, **kwargs):
    return trans_request(request, HERMES, token=token)


@bp.get('/applicant/<email>')
@jwt_required(allow=[ADMIN, ROOT_ADMIN, ])
async def applicant_email_patch(request: Request, token: Token, email: str, *args, **kwargs):
    return trans_request(request, HERMES, token=token)


@bp.delete('/applicant/<email>')
@jwt_required(allow=[ROOT_ADMIN, ADMIN, ])
async def applicant_email_patch(request: Request, token: Token, email: str, *args, **kwargs):
    return trans_request(request, HERMES, token=token)


@bp.get('/applicant/<email>/status')
@jwt_required(allow=[ROOT_ADMIN, ADMIN, ])
async def applicant_email_patch(request: Request, token: Token, email: str, *args, **kwargs):
    return trans_request(request, HERMES, token=token)


@bp.patch('/applicant/<email>/status')
@jwt_required(allow=[ROOT_ADMIN, ADMIN, ])
async def applicant_email_patch(request: Request, token: Token, email: str, *args, **kwargs):
    return trans_request(request, HERMES, token=token)


@bp.get('/applicant/me')
@jwt_required(allow=[APPLICANT, ])
async def applicant_me_get(request: Request, token: Token, *args, **kwargs):
    return trans_request(request, HERMES, f"/applicant/{token.jwt_identity}", token=token)


@bp.patch('/applicant/me')
@jwt_required(allow=[APPLICANT, ])
async def applicant_me_patch(request: Request, token: Token, *args, **kwargs):
    return trans_request(request, HERMES, f"/applicant/{token.jwt_identity}", token=token)


@bp.get('/applicant/me/status')
@jwt_required(allow=[APPLICANT, ])
async def applicant_me_patch(request: Request, token: Token, *args, **kwargs):
    return trans_request(request, HERMES, f"/applicant/{token.jwt_identity}", token=token)


"""
Photo API
"""


@bp.put('/applicant/me/photo')
@jwt_required(allow=[APPLICANT, ])
async def applicant_me_photo_put(request: Request, token: Token, *args, **kwargs):
    if not os.path.exists(UPLOAD_DIR):
        os.makedirs(UPLOAD_DIR)

    file = request.files.get('file')
    if not file:
        return json({"msg": "file required"}, status=400)

    ext = file.name.split(".")[-1]
    if ext not in ["png", "jpeg", "jpg", 'jp2', 'j2c']:
        return json({"msg": f"{ext} type file is not allowed"}, status=400)

    filename = f"{uuid.uuid4().hex}.{ext}"

    async with aiofiles.open(f"{UPLOAD_DIR}/{filename}", 'wb') as f:
        await f.write(file.body)
    f.close()

    try:
        r = requests.patch(
            url=f"{HERMES}/api/v1/applicant/{token.jwt_identity}",
            data={
                "image_path": filename
            }
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

    return json({"image_path": filename}, status=201)


@bp.get('/applicant/<email>/photo')
@jwt_required(allow=[ADMIN, ROOT_ADMIN, ])
async def applicant_me_photo_get(request: Request, token: Token, email: str, *args, **kwargs):
    try:
        r = requests.get(
            url=f"{HERMES}/api/v1/applicant/{email}",
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

    filename = r.json()["image_path"]
    if not filename:
        return HTTPResponse(status=204)

    return file(f"{UPLOAD_DIR}/{filename}", status=201)


@bp.get('/applicant/me/photo')
@jwt_required(allow=[APPLICANT, ])
async def applicant_me_photo_get(request: Request, token: Token, *args, **kwargs):
    try:
        r = requests.get(
            url=f"{HERMES}/api/v1/applicant/{token.jwt_identity}",
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

    filename = r.json()["image_path"]
    if not filename:
        return HTTPResponse(status=204)

    return file(f"{UPLOAD_DIR}/{filename}", status=201)


"""
Louis-Vuitton Routing
"""


@bp.get('/applicant/<email>/classification')
@jwt_required(allow=[ADMIN, ROOT_ADMIN, ])
async def applicant_email_classification_get(request: Request, token: Token, email: str, *args, **kwargs):
    return trans_request(request, LV, token=token)


@bp.patch('/applicant/<email>/classification')
@jwt_required(allow=[ADMIN, ROOT_ADMIN, ])
async def applicant_email_classification_patch(request: Request, token: Token, email: str, *args, **kwargs):
    return trans_request(request, LV, token=token)


@bp.get('/applicant/me/classification')
@jwt_required(allow=[APPLICANT, ])
async def applicant_me_classification_get(request: Request, token: Token, *args, **kwargs):
    return trans_request(request, LV, f"/applicant/{token.jwt_identity}/classification", token=token)


@bp.patch('/applicant/me/classification')
@jwt_required(allow=[APPLICANT, ])
async def applicant_me_classification_patch(request: Request, token: Token, *args, **kwargs):
    return trans_request(request, LV, f"/applicant/{token.jwt_identity}/classification", token=token)


@bp.get('/applicant/<email>/document')
@jwt_required(allow=[ADMIN, ROOT_ADMIN, ])
async def applicant_email_document_get(request: Request, token: Token, email: str, *args, **kwargs):
    return trans_request(request, LV, token=token)


@bp.patch('/applicant/<email>/document')
@jwt_required(allow=[ADMIN, ROOT_ADMIN, ])
async def applicant_email_document_patch(request: Request, token: Token, email: str, *args, **kwargs):
    return trans_request(request, LV, token=token)


@bp.get('/applicant/me/document')
@jwt_required(allow=[APPLICANT, ])
async def applicant_me_document_get(request: Request, token: Token, *args, **kwargs):
    return trans_request(request, LV, f"/applicant/{token.jwt_identity}/document", token=token)


@bp.patch('/applicant/me/document')
@jwt_required(allow=[APPLICANT, ])
async def applicant_me_document_patch(request: Request, token: Token, *args, **kwargs):
    return trans_request(request, LV, f"/applicant/{token.jwt_identity}/document", token=token)


@bp.get('/applicant/<email>/diligence')
@jwt_required(allow=[ADMIN, ROOT_ADMIN, ])
async def applicant_email_diligence_get(request: Request, token: Token, email: str, *args, **kwargs):
    return trans_request(request, LV, token=token)


@bp.patch('/applicant/<email>/diligence')
@jwt_required(allow=[ADMIN, ROOT_ADMIN, ])
async def applicant_email_diligence_patch(request: Request, token: Token, email: str, *args, **kwargs):
    return trans_request(request, LV, token=token)


@bp.get('/applicant/<email>/ged-score')
@jwt_required(allow=[ADMIN, ROOT_ADMIN, ])
async def applicant_email_ged_score_get(request: Request, token: Token, email: str, *args, **kwargs):
    return trans_request(request, LV, token=token)


@bp.patch('/applicant/<email>/ged-score')
@jwt_required(allow=[ADMIN, ROOT_ADMIN, ])
async def applicant_email_ged_score_patch(request: Request, token: Token, email: str, *args, **kwargs):
    return trans_request(request, LV, token=token)


@bp.get('/applicant/<email>/academic-score')
@jwt_required(allow=[ADMIN, ROOT_ADMIN, ])
async def applicant_email_academic_score_get(request: Request, token: Token, email: str, *args, **kwargs):
    return trans_request(request, LV, token=token)


@bp.patch('/applicant/<email>/academic-score')
@jwt_required(allow=[ADMIN, ROOT_ADMIN, ])
async def applicant_email_academic_score_patch(request: Request, token: Token, email: str, *args, **kwargs):
    return trans_request(request, LV, token=token)
