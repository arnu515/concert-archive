from functools import wraps

from sanic import json

from .tokens import get_user_from_access_token


def get_token_from_header(auth_header: str):
    if not auth_header:
        return None
    if not auth_header.lower().startswith("bearer "):
        return None
    return auth_header[7:].strip() or None


def auth(required=True):
    def decorator(func):
        @wraps(func)
        async def wrapper(request, *args, **kwargs):
            token = get_token_from_header(request.headers.get("Authorization"))
            if not token:
                if required:
                    return json({"message": "Invalid token"}, status=401)
                return await func(request, *args, **kwargs)
            user = await get_user_from_access_token(token)
            if not user and required:
                return request.ctx.response.json({"message": "Unauthorized"}, status=401)
            request.ctx.user = user
            request.ctx.safe_user = {
                "email": user.email,
                "username": user.username,
                "avatar_url": user.avatar_url,
                "id": user.id
            }
            return await func(request, *args, **kwargs)

        return wrapper

    return decorator
