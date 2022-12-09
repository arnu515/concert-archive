import datetime
import os
from dataclasses import dataclass, asdict, fields
from functools import wraps
from hashlib import sha256
from json import loads, dumps
from random import choice
from typing import TypedDict

import jwt
from prisma.models import Users, Stages
from sanic import json

from .colors import colors


@dataclass
class VideoGrant:
    # permission to create a room
    roomCreate: bool

    # permission to join a room as a participant, room must be set
    roomJoin: bool

    # permission to list rooms
    roomList: bool

    # permission to start a recording
    roomRecord: bool

    # permission to control a specific room, room must be set
    roomAdmin: bool

    # name of the room, must be set for admin or join permissions
    room: str

    # permissions to control ingress, not specific to any room or ingress
    ingressAdmin: bool

    # allow participant to publish. If neither canPublish or canSubscribe is set,
    # both publish and subscribe are enabled
    canPublish: bool

    # allow participant to subscribe to other tracks
    canSubscribe: bool

    # allow participants to publish data, defaults to true if not set
    canPublishData: bool

    # participant isn't visible to others
    hidden: bool

    # participant is recording the room, when set, allows room to indicate it's being recorded
    recorder: bool


class Metadata(TypedDict):
    username: str
    avatar: str
    id: str
    joined_at: str
    color: str


@dataclass
class ClaimGrants:
    name: str
    video: VideoGrant
    metadata: str
    sha256: str

    def __init__(self, **kwargs):
        names = set([f.name for f in fields(self)])
        for k, v in kwargs.items():
            if k in names:
                setattr(self, k, v)

    @property
    def parsed_metadata(self) -> Metadata:
        return loads(self.metadata)


def get_metadata(user: Users) -> str:
    return dumps({
        "username": user.username,
        "avatar_url": user.avatar_url,
        "id": user.id,
        "joined_at": datetime.datetime.utcnow().isoformat(),
        "color": choice(colors)
    })


def create_livekit_token(user: Users, stage: Stages, can_speak: bool = False):
    """**Assumes that the user is allowed to join the stage**"""
    grants = ClaimGrants(
        name=user.username,
        video=VideoGrant(
            roomCreate=False,
            roomJoin=True,
            roomList=False,
            roomAdmin=stage.owner_id == user.id,
            roomRecord=False,
            room=stage.id,
            canPublish=can_speak,
            canPublishData=False,
            canSubscribe=True,
            hidden=False,
            recorder=False,
            ingressAdmin=False
        ),
        metadata=get_metadata(user),
        sha256=sha256(f"{user.id}_{stage.id}".encode()).hexdigest()
    )

    payload = {
        **asdict(grants),
        "sub": user.id,
        "iss": os.getenv("LIVEKIT_KEY"),
        "jwtid": user.id,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    }

    token = jwt.encode(payload, os.getenv("LIVEKIT_SECRET"), algorithm="HS256")
    return token


def create_server_token(stage_id: str):
    """Creates a server token with admin access"""
    grants = ClaimGrants(
        name="server",
        video=VideoGrant(
            roomCreate=True,
            roomJoin=True,
            roomList=True,
            roomAdmin=True,
            roomRecord=True,
            room=stage_id,
            canPublish=True,
            canPublishData=True,
            canSubscribe=True,
            hidden=True,
            recorder=True,
            ingressAdmin=True
        ),
        metadata=dumps({
        }),
        sha256=sha256(f"server_{stage_id}".encode()).hexdigest()
    )

    payload = {
        **asdict(grants),
        "sub": "server",
        "iss": os.getenv("LIVEKIT_KEY"),
        "jwtid": "server",
        "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=1)
    }

    token = jwt.encode(payload, os.getenv("LIVEKIT_SECRET"), algorithm="HS256")
    return token


def validate_token(token: str):
    try:
        return jwt.decode(token, os.getenv("LIVEKIT_SECRET"), algorithms=["HS256"])
    except jwt.exceptions.InvalidTokenError:
        return None


def livekit(required=True):
    def decorator(func):
        @wraps(func)
        async def wrapper(request, *args, **kwargs):
            if not request.ctx.user:
                return json({"error": "Unauthorized"}, 401)
            token = request.headers.get("x-livekit-token")
            if not token:
                if required:
                    return json({"message": "Invalid livekit token"}, status=401)
                return await func(request, *args, **kwargs)
            payload = validate_token(token)
            if not payload and required:
                return json({"message": "Not in stage"}, status=401)
            if payload:
                if request.ctx.user.id != payload['sub']:
                    return json({"error": "Unauthorized"}, 401)
                try:
                    grants = ClaimGrants(**payload)
                    request.ctx.grants = grants
                except TypeError:
                    return json({"error": "Invalid livekit token"}, 401)
            return await func(request, *args, **kwargs)

        return wrapper

    return decorator
