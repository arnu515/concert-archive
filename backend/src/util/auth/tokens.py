import datetime
import os

from jwt import encode, PyJWTError, decode
from prisma.models import Users

from src.util.db import db

JWT_SECRET = os.getenv("JWT_SECRET", "secret")
JWT_EXPIRY = int(os.getenv("JWT_EXPIRY", 900))


def generate_access_token(user: Users):
    return encode(
        {
            "id": user.id,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(seconds=JWT_EXPIRY),
        },
        JWT_SECRET,
        algorithm="HS256",
    )


async def get_user_from_access_token(token: str) -> Users | None:
    try:
        decoded = decode(token, JWT_SECRET, algorithms=["HS256"])
        return await db.users.find_unique({"id": decoded["id"]}) or None
    except PyJWTError as e:
        print(e)
        return None


async def generate_refresh_token(user: Users):
    token = await db.refreshtokens.create({"user": {"connect": {"id": user.id}}})
    return token.token


async def get_access_token_from_refresh_token(refresh_token: str):
    token = await db.refreshtokens.find_unique({"token": refresh_token}, {"user": True})
    if not token:
        return None
    if token.created_at.replace(tzinfo=None) < (datetime.datetime.utcnow() - datetime.timedelta(days=30)).replace(
            tzinfo=None):
        return None
    return generate_access_token(token.user)


async def revoke_refresh_token(refresh_token: str):
    await db.refreshtokens.delete({"token": refresh_token})
