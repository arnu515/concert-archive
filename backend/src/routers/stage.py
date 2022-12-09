from dataclasses import asdict
from json import loads, dumps

from livekit import DataPacketKind, ParticipantPermission
from sanic import Blueprint, Request, json
from sanic.request import File

from src.util.auth import auth
from src.util.b2 import upload_file
from src.util.db import db
from src.util.livekit.client import client
from src.util.livekit.token import create_livekit_token, livekit, ClaimGrants

router = Blueprint("stage", "/api/stage/<sid:str>")


@router.get("/token")
@auth()
async def get_stage_token(req: Request, sid: str):
    uid = req.ctx.user.id if hasattr(req.ctx, "user") else None
    if not uid:
        return json({"message": "Unauthorized"}, status=401)
    stage = await db.stages.find_first(
        where={"id": sid, "OR": [{"invites": {"some": {"user_id": uid}}}, {"owner_id": uid}, {"private": False}]},
        include={"owner": True}
    )
    if not uid and stage.private:
        return json({"message": "Stage not found. You may need to login to access private stages"}, status=404)
    if not stage:
        return json({"message": "Stage not found. You may need to login to access private stages"}, status=404)

    token = create_livekit_token(req.ctx.user, stage, stage.owner_id == req.ctx.user.id)
    return json({"token": token})


@router.get("/info")
@auth()
@livekit()
async def get_stage_info(req: Request, sid: str):
    if req.ctx.grants.video["room"] != sid:
        return json({"message": "Invalid livekit token"}, status=401)

    return json(asdict(req.ctx.grants))


@router.get("/chat")
@auth()
@livekit()
async def get_chat(request: Request, sid: str):
    grants: ClaimGrants = request.ctx.grants
    if grants.video["room"] != sid:
        return json({"message": "Invalid livekit token"}, status=401)

    messages = await db.chatmessages.find_many(where={"stage_id": sid}, include={"user": True}, take=100,
                                               order={"created_at": "asc"})
    return json({"messages": [loads(x.json()) for x in messages]})


@router.post("/chat")
@auth()
@livekit()
async def chat(request: Request, sid: str):
    grants: ClaimGrants = request.ctx.grants
    if grants.video["room"] != sid:
        return json({"message": "Invalid livekit token"}, status=401)

    body = request.json

    if not body:
        return json({"message": "Missing body"}, status=400)
    if type(body.get("message")) != str or not body["message"].strip():
        return json({"message": "Missing message"}, status=400)
    if len(body["message"].strip()) > 512:
        return json({"message": "Message must be less than 512 chars"}, status=400)

    msg = await db.chatmessages.create({
        "type": "TEXT",
        "message_data": body["message"].strip(),
        "stage_id": sid,
        "user_id": request.ctx.user.id,
    }, include={"user": True})

    client.send_data(sid, dumps({"type": "CHAT", "data": loads(msg.json())}).encode(), DataPacketKind.RELIABLE, [])

    return json({"id": msg.id})


@router.post("/chat/file")
@auth()
@livekit()
async def chat_file(request: Request, sid: str):
    grants: ClaimGrants = request.ctx.grants
    if grants.video["room"] != sid:
        return json({"message": "Invalid livekit token"}, status=401)

    file: File = request.files.get("file")
    if not file:
        return json({"message": "Missing file"}, status=400)
    if len(file.body) > 2 * 1024 * 1024:
        return json({"message": "File must be less than 2MiB"}, status=400)

    url = upload_file(file.body, file.name, file.type)

    msg = await db.chatmessages.create({
        "type": "FILE",
        "message_data": url,
        "stage_id": sid,
        "user_id": request.ctx.user.id,
    })

    client.send_data(sid, dumps({"type": "CHAT", "data": loads(msg.json())}).encode(), DataPacketKind.RELIABLE, [])

    return json({"id": msg.id})


@router.post("/request_to_speak")
@auth()
@livekit()
async def request_to_speak(request: Request, sid: str):
    grants: ClaimGrants = request.ctx.grants
    if grants.video["room"] != sid:
        return json({"message": "Invalid livekit token"}, status=401)

    msg = await db.chatmessages.create({
        "type": "EVENT",
        "message_data": "REQUEST_TO_SPEAK",
        "stage_id": sid,
        "user_id": request.ctx.user.id,
    }, include={"user": True})

    client.send_data(sid, dumps({"type": "CHAT", "data": loads(msg.json())}).encode(), DataPacketKind.RELIABLE, [])

    return json({"message": "Request sent"})


async def toggle_speaker(request: Request, sid: str, is_speaker: bool):
    grants: ClaimGrants = request.ctx.grants
    if grants.video["room"] != sid:
        return json({"message": "Invalid livekit token"}, status=401)
    stage = await db.stages.find_first(where={"id": sid})
    if request.ctx.user.id != stage.owner_id:
        return json({"message": "You are not the owner"}, status=401)

    body = request.json
    if not body:
        return json({"message": "Missing body"}, status=401)
    if type(body.get("user_id")) != str:
        return json({"message": "Missing user_id"}, status=401)

    user = await db.users.find_first(where={"id": body["user_id"]})
    if not user:
        return json({"message": "User not found"}, status=404)

    perm = ParticipantPermission(
        can_subscribe=True,
        can_publish=is_speaker,
        can_publish_data=False,
        recorder=False,
        hidden=False
    )
    client.update_participant(sid, user.id, permission=perm)

    msg = await db.chatmessages.create({
        "type": "EVENT",
        "message_data": "MADE_SPEAKER" if is_speaker else "MADE_LISTENER",
        "stage_id": sid,
        "user_id": user.id,
    }, include={"user": True})

    client.send_data(sid, dumps({"type": "CHAT", "data": loads(msg.json())}).encode(), DataPacketKind.RELIABLE, [])

    return json({"message": "Promoted to speaker"})


@router.post("/owner/make_speaker")
@auth()
@livekit()
async def make_speaker(request: Request, sid: str):
    return await toggle_speaker(request, sid, True)


@router.post("/owner/make_listener")
@auth()
@livekit()
async def make_listener(request: Request, sid: str):
    return await toggle_speaker(request, sid, False)
