from functools import wraps
from typing import List

from sanic.request import Request
from sanic.response import json
from sanic_jwt_extended import jwt_required
from sanic_jwt_extended.tokens import Token


def auth(eligible_authority: List[str]):
    def decorator(fn):
        @wraps(fn)
        @jwt_required
        async def wrapper(request: Request, token: Token, *args, **kwargs):
            authority = token.raw_jwt["authority"]
            if authority in eligible_authority:
                return await fn(request, token, *args, **kwargs)

            return json({"msg": "Authentication failed"}, status=401)
        return wrapper
    return decorator
