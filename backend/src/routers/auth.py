import os
from datetime import datetime, timedelta
from json import loads
from urllib.parse import urlparse
from uuid import uuid4 as uuid

from sanic import Blueprint, Request, json, redirect

from src.util.auth import auth
from src.util.auth.providers import providers
from src.util.auth.tokens import generate_refresh_token, get_access_token_from_refresh_token
from src.util.db import db

router = Blueprint("auth", "/api/auth")


async def save_state(state: str):
    await db.oauthstates.create({"state": state})


async def delete_state(state: str):
    await db.oauthstates.delete({"state": state})


async def check_state(state: str):
    data = await db.oauthstates.find_unique({"state": state})
    if data and data.created_at.replace(tzinfo=None) < (datetime.utcnow() - timedelta(minutes=15)).replace(
            tzinfo=None):
        return False
    return data is not None


@router.get("/<provider:str>/oauth")
async def redirect_to_oauth(_, provider: str):
    provider_cls = providers.get(provider)
    if not provider_cls:
        return json({"message": "Invalid provider"}, status=404)
    state = str(uuid())
    await save_state(state)
    return redirect(
        f"{provider_cls.auth_url}?client_id={provider_cls.client_id}&scope={provider_cls.scopes}&state={state}")


@router.get("/<provider:str>/callback")
async def callback(req: Request, provider: str):
    provider_cls = providers.get(provider)
    if not provider_cls:
        return json({"message": "Invalid provider"}, status=404)
    code = req.args.get("code")
    if not code:
        return json({"message": "No code provided"}, status=400)
    state = req.args.get("state")
    if not state:
        return json({"message": "No state provided"}, status=400)
    if not await check_state(state):
        return json({"message": "Invalid state"}, status=400)
    token = await provider_cls.get_token(code)
    if type(token) == str:
        return json({"message": token}, status=400)
    user_data = await provider_cls.get_user_info(token["access_token"], token["refresh_token"])
    if type(user_data) == str:
        return json({"message": token}, status=400)
    user = await db.users.find_unique({"email": user_data["email"]})
    if not user:
        user = await db.users.create(user_data)
    else:
        if user.provider != provider_cls.name:
            return json({
                "message": "User already exists with different provider. Please login using \"" + user.provider + "\""},
                status=400)
        if user.provider_id != user_data["provider_id"]:
            return json({
                "message": "Invalid account. Please contact support. Your email does not match your \"" + user.provider + "\" id"},
                status=400)
    await delete_state(state)

    code = await db.oauthcodes.create({"user": {"connect": {"id": user.id}}})
    return redirect(f"{os.getenv('FRONTEND_URL')}?code={code.code}")


@router.get("/me")
@auth()
async def get_user(req: Request):
    return json({"user": loads(req.ctx.safe_user.json())})


@router.post("/refresh/token")
async def set_token_from_code(req: Request):
    if not req.json:
        return json({"message": "No body provided"}, status=400)
    code = req.json.get("code")
    if not code:
        return json({"message": "No code provided"}, status=400)
    code = await db.oauthcodes.find_unique({"code": code})
    if not code:
        return json({"message": "Invalid code"}, status=400)
    await db.oauthcodes.delete({"code": code.code})
    user = await db.users.find_unique({"id": code.user_id})
    if not user:
        return json({"message": "User not found"}, status=400)

    refresh_token = await generate_refresh_token(user)

    res = json({"refresh_token": refresh_token})
    res.cookies["refresh_token"] = refresh_token
    res.cookies["refresh_token"]["httponly"] = True
    res.cookies["refresh_token"]["samesite"] = not bool(os.getenv("DEV"))
    res.cookies["refresh_token"]["secure"] = os.getenv("SELF_URL").startswith("https://")
    res.cookies["refresh_token"]["max-age"] = 60 * 60 * 24 * 30
    res.cookies["refresh_token"]["path"] = "/api/auth/refresh"
    res.cookies["refresh_token"]["domain"] = urlparse(os.getenv("SELF_URL")).hostname

    return res


@router.route("/refresh", methods=["GET", "POST"])
async def refresh(req: Request):
    print(req.cookies)
    token_from_cookie = req.cookies.get("refresh_token")
    if not token_from_cookie or type(token_from_cookie) != str:
        res = json({"message": "Unauthorized"}, status=401)
        del res.cookies["refresh_token"]
        return res
    token = await get_access_token_from_refresh_token(token_from_cookie)
    if not token:
        res = json({"message": "Invalid refresh token"}, status=400)
        del res.cookies["refresh_token"]
        return res
    return json({"access_token": token, "refresh_token": token_from_cookie})


@router.route("/refresh/invalidate", methods=["GET", "POST"])
async def invalidate(req: Request):
    token_from_cookie = req.cookies.get("refresh_token")
    if not token_from_cookie or type(token_from_cookie) != str:
        res = json({"message": "Unauthorized"}, status=401)
        del res.cookies["refresh_token"]
        return res
    await db.refreshtokens.delete({"token": token_from_cookie})
    res = json({"message": "Success"})
    del res.cookies["refresh_token"]
    return res
