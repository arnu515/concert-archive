from typing import Any

from bcrypt import hashpw, gensalt
from prisma.partials import SafeStage
from pydantic import BaseModel, validator
from sanic import Blueprint, Request, json
from sanic_ext import validate

from src.util.auth import auth
from src.util.db import db

router = Blueprint("stages", "/api/stages")


class CreateStageRequest(BaseModel):
    name: str = ...
    password: str | None = None
    color: str = "#00a9a5"
    private: bool = False

    @classmethod
    @validator('color')
    def color_validator(cls, value: Any) -> str | None:
        if value is None:
            return None
        if type(value) != str:
            raise ValueError("Color must be a string")
        if not value.strip().startswith("#"):
            raise ValueError("Color must start with #")
        if len(value.strip()) != 7:
            raise ValueError("Color must be 6 characters long")
        if not all(c in "0123456789abcdef" for c in value[1:]):
            raise ValueError("Color must be a valid hex color")
        return value.lower().strip()

    @classmethod
    @validator('private')
    def private_validator(cls, value: Any) -> bool:
        return bool(value)

    @classmethod
    @validator('name')
    def name_validator(cls, value: Any) -> str:
        if type(value) != str:
            raise ValueError("Name must be a string")
        if len(value.strip()) < 1:
            raise ValueError("Name must be at least 1 character long")
        return value.strip()

    @classmethod
    @validator('password')
    def password_validator(cls, value: Any) -> str | None:
        if value is None:
            return None
        if type(value) != str:
            raise ValueError("Password must be a string")
        if len(value.strip()) < 1:
            raise ValueError("Password must be at least 1 character long")
        return value.strip()


@router.post("/")
@auth()
@validate(json=CreateStageRequest)
async def create_stage(req: Request, body: CreateStageRequest):
    stage = await db.stages.create({
        "name": body.name,
        "password": hashpw(body.password.encode(), gensalt(12)).decode() if body.password is not None else None,
        "color": body.color,
        "private": body.private,
        "owner_id": req.ctx.user.id
    })
    return json({"stage": SafeStage(**stage.dict()).dict()})
