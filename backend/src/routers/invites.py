from json import loads

from prisma.partials import SafeStage
from pydantic import BaseModel
from sanic import Blueprint, Request, json
from sanic_ext import validate

from src.util.auth import auth
from src.util.db import db

router = Blueprint("invites", url_prefix="/api/invites")


@router.get("/")
@auth()
async def get_all_invites(req: Request):
    invites = await db.invites.find_many(where={"user_id": req.ctx.user.id}, include={"stage": True})
    return json({"invites": [{**loads(invite.json()), "stage": loads(SafeStage(**invite.stage.dict()).json())} for
                             invite in invites]})


@router.get("/<iid:str>")
@auth()
async def get_invite_by_id(req: Request, iid: str):
    invite = await db.invites.find_first(where={"id": iid, "user_id": req.ctx.user.id}, include={"stage": True})
    print(invite)
    if not invite:
        return json({"message": "Invite not found"}, status=404)
    return json({"invite": {**loads(invite.json()), "stage": loads(SafeStage(**invite.stage.dict()).json())}})


class CreateInviteRequest(BaseModel):
    stage_id: str = ...
    user_id: str = ...


@router.post("/")
@auth()
@validate(json=CreateInviteRequest)
async def create_invite(req: Request, body: CreateInviteRequest):
    if body.user_id == req.ctx.user.id:
        return json({"message": "You can't invite yourself"}, status=400)
    stage = await db.stages.find_first(where={"id": body.stage_id, "owner_id": req.ctx.user.id})
    if not stage:
        return json({"message": "Stage not found"}, status=404)
    invite = await db.invites.create({"user_id": body.user_id, "stage_id": stage.id},
                                     include={"stage": True})
    return json({"invite": {**loads(invite.json()), "stage": loads(SafeStage(**invite.stage.dict()).json())}})


@router.delete("/<iid:str>")
@auth()
async def delete_invite(req: Request, iid: str):
    invite = await db.invites.find_first(where={"id": iid, "user_id": req.ctx.user.id}, include={"stage": True})
    if not invite:
        return json({"message": "Invite not found"}, status=404)
    await db.invites.delete(where={"id": iid})
    return json({"invite": {**loads(invite.json()), "stage": loads(SafeStage(**invite.stage.dict()).json())}})
