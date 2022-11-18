from datetime import datetime, timedelta
from uuid import uuid4 as uuid

from sanic import Blueprint, Request, json, redirect

from src.util.auth import auth
from src.util.auth.providers import providers
from src.util.auth.tokens import generate_access_token, generate_refresh_token, get_access_token_from_refresh_token
from src.util.db import db

router = Blueprint("auth", "/api/auth")


async def save_state(state: str):
    await db.oauthstates.create({"state": state})


async def delete_state(state: str):
    await db.oauthstates.delete({"state": state})


async def check_state(state: str):
    data = await db.oauthstates.find_unique({"state": state})
    if data and data.createdAt.replace(tzinfo=None) < (datetime.utcnow() - timedelta(minutes=15)).replace(
            tzinfo=None):
        return False
    return data is not None


@router.get("/<provider:str>/oauth")
async def redirect_to_oauth(req: Request, provider: str):
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

    return json({"access_token": generate_access_token(user), "refresh_token": await generate_refresh_token(user)})


@router.get("/me")
@auth()
async def get_user(req: Request):
    return json({"user": req.ctx.safe_user})


@router.post("/refresh")
async def refresh(req: Request):
    if not req.json or type(req.json.get("refresh_token")) != str:
        return json({"message": "No refresh token provided"}, status=400)
    token = await get_access_token_from_refresh_token(req.json["refresh_token"])
    if not token:
        return json({"message": "Invalid refresh token"}, status=400)
    return json({"access_token": token, "refresh_token": req.json["refresh_token"]})


@router.post("/refresh/invalidate")
async def invalidate(req: Request):
    if not req.json or type(req.json.get("refresh_token")) != str:
        return json({"message": "No refresh token provided"}, status=400)
    await db.refreshtokens.delete({"token": req.json.get("refresh_token")})
    return json({"message": "Success"})
