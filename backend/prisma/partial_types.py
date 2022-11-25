from prisma.models import Stages, Users

Users.create_partial("SafeUser", {"id", "email", "username", "avatar_url", "created_at"})

Stages.create_partial("SafeStage", {"id", "name", "color", "private", "owner_id", "owner"}, optional={"owner"})
