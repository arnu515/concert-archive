from json import loads
from typing import Any

from bcrypt import hashpw, gensalt
from prisma.partials import SafeStage, SafeUser
from pydantic import BaseModel, validator
from sanic import Blueprint, Request, json
from sanic_ext import validate

from concert_backend.util.auth import auth
from concert_backend.util.db import db

router = Blueprint("stages", "/api/stages")


@router.get("/")
async def get_public_stages(req: Request):
    limit = type(req.args.get("limit")) == str and int(req.args.get("limit")) or 10
    offset = type(req.args.get("offset")) == str and int(req.args.get("offset")) or 0
    sort = type(req.args.get("sort")) == str and req.args.get("sort") or "created_at"
    sort_order = type(req.args.get("sort_order")) == str and req.args.get("sort_order").lower()
    if sort_order not in ("asc", "desc"):
        sort_order = "desc"

    stages = await db.stages.find_many(
        where={"private": False},
        take=limit,
        skip=offset,
        order={sort: sort_order},
        include={"owner": True}
    )
    return json([loads(SafeStage(**stage.dict()).json()) for stage in stages])


@router.get('/all')
@auth(False)
async def get_all_stages(req: Request):
    limit = type(req.args.get("limit")) == str and int(req.args.get("limit")) or 10
    offset = type(req.args.get("offset")) == str and int(req.args.get("offset")) or 0
    sort = type(req.args.get("sort")) == str and req.args.get("sort") or "created_at"
    sort_order = type(req.args.get("sort_order")) == str and req.args.get("sort_order").lower()
    if sort_order not in ("asc", "desc"):
        sort_order = "desc"

    uid = req.ctx.user.id if hasattr(req.ctx, "user") else None
    stages = await db.stages.find_many(
        where={"OR": [{"invites": {"some": {"user_id": uid}}}, {"owner_id": uid}, {"private": False}]} if uid else {
            "private": False},
        take=limit,
        skip=offset,
        order={sort: sort_order},
        include={"owner": True}
    )
    return json({"stages": [loads(SafeStage(**stage.dict()).json()) for stage in stages]})


@router.get("/<sid:str>")
@auth(False)
async def get_stage_by_id(req: Request, sid: str):
    uid = req.ctx.user.id if hasattr(req.ctx, "user") else None
    stage = await db.stages.find_first(
        where={"id": sid,
               "OR": [{"invites": {"some": {"user_id": uid}}}, {"owner_id": uid}, {"private": False}]} if uid else {
            "id": sid},
        include={"owner": True}
    )
    if not uid and stage.private:
        return json({"message": "Stage not found. You may need to login to access private stages"}, status=404)
    if not stage:
        return json({"message": "Stage not found. You may need to login to access private stages"}, status=404)
    return json({"stage": loads(SafeStage(**stage.dict()).json())})


@router.get('/by/<uid:str>')
async def get_stages_by_uid(req: Request, uid: str):
    limit = type(req.args.get("limit")) == str and int(req.args.get("limit")) or 10
    offset = type(req.args.get("offset")) == str and int(req.args.get("offset")) or 0
    sort = type(req.args.get("sort")) == str and req.args.get("sort") or "created_at"
    sort_order = type(req.args.get("sort_order")) == str and req.args.get("sort_order").lower()
    if sort_order not in ("asc", "desc"):
        sort_order = "desc"

    stages = await db.stages.find_many(
        where={"private": False, "owner_id": uid},
        take=limit,
        skip=offset,
        order={sort: sort_order},
        include={"owner": True}
    )
    return json([loads(SafeStage(**stage.dict()).json()) for stage in stages])


@router.get('/all/by/<uid:str>')
@auth(False)
async def get_all_stages_by_uid(req: Request, uid: str):
    limit = type(req.args.get("limit")) == str and int(req.args.get("limit")) or 10
    offset = type(req.args.get("offset")) == str and int(req.args.get("offset")) or 0
    sort = type(req.args.get("sort")) == str and req.args.get("sort") or "created_at"
    sort_order = type(req.args.get("sort_order")) == str and req.args.get("sort_order").lower()
    if sort_order not in ("asc", "desc"):
        sort_order = "desc"

    cuid = req.ctx.user.id if hasattr(req.ctx, "user") else None
    if not cuid:
        query = {"private": False}
    if cuid == uid:
        query = {"owner_id": cuid, "private": False}
    else:
        query = {"invites": {"some": {"user_id": cuid}}, "owner_id": uid, "private": False}
    stages = await db.stages.find_many(
        where=query,
        take=limit,
        skip=offset,
        order={sort: sort_order},
        include={"owner": True}
    )
    return json({"stages": [loads(SafeStage(**stage.dict()).json()) for stage in stages]})


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
    }, include={"owner": True})
    s = SafeStage(**stage.dict())
    s.owner = SafeUser(**stage.owner.dict())
    return json({"stage": loads(s.json())})


class UpdateStageRequest(CreateStageRequest):
    name: str | None
    use_password_in_body: bool = False

    @classmethod
    @validator('name')
    def name_validator(cls, value: Any) -> str | None:
        if value is None:
            return None
        if type(value) != str:
            raise ValueError("Name must be a string")
        if len(value.strip()) < 1:
            raise ValueError("Name must be at least 1 character long")
        return value.strip()

    @classmethod
    @validator('use_password_in_body')
    def use_password_in_body_validator(cls, value: Any) -> True:
        return bool(value)


@router.put("/<sid:str>")
@auth()
@validate(json=UpdateStageRequest)
async def update_stage(req: Request, body: UpdateStageRequest, sid: str):
    stage = await db.stages.find_unique(where={"id": sid})
    if not stage:
        return json({"message": "Stage not found"}, status=404)
    if stage.owner_id != req.ctx.user.id:
        return json({"message": "You don't have access to this stage"}, status=403)
    password_up = {}
    if body.use_password_in_body:
        password_up = {
            "password": hashpw(body.password.encode(), gensalt(12)).decode() if body.password is not None else None}
    stage = await db.stages.update({
        "name": body.name or stage.name,
        "color": body.color,
        "private": body.private,
        **password_up
    }, {"id": sid}, include={"owner": True})
    return json({"stage": loads(SafeStage(**stage.dict()).json())})


@router.delete("/<sid:str>")
@auth()
async def delete_stage(req: Request, sid: str):
    stage = await db.stages.find_unique(where={"id": sid}, include={"owner": True})
    if not stage:
        return json({"message": "Stage not found"}, status=404)
    if stage.owner_id != req.ctx.user.id:
        return json({"message": "You don't have access to this stage"}, status=403)
    await db.stages.delete({"id": sid})
    return json({"stage": loads(SafeStage(**stage.dict()).json())})
