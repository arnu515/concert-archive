import os
from abc import abstractmethod

from httpx import AsyncClient


class Provider:
    name: str
    api_url: str
    auth_url: str
    token_url: str
    scopes: str

    @classmethod
    @abstractmethod
    async def get_token(cls, code: str):
        pass

    @classmethod
    @abstractmethod
    async def get_user_info(cls, access_token: str, refresh_token: str):
        pass

    @classmethod
    @abstractmethod
    async def revoke_token(cls, access_token: str, refresh_token: str):
        pass


class GitHub(Provider):
    name = "github"
    api_url = "https://api.github.com"
    auth_url = "https://github.com/login/oauth/authorize"
    token_url = "https://github.com/login/oauth/access_token"
    scopes = "user:email"
    client_id = os.getenv("GITHUB_CLIENT_ID")
    client_secret = os.getenv("GITHUB_CLIENT_SECRET")

    @classmethod
    async def get_token(cls, code: str):
        async with AsyncClient() as client:
            response = await client.post(cls.token_url, json={
                "client_id": cls.client_id,
                "client_secret": cls.client_secret,
                "code": code,
                "redirect_urL": f"{os.getenv('SELF_URL')}/api/auth/github/callback"
            }, headers={"Accept": "application/json"})
            data = response.json()
            if type(data) == dict and data.get("access_token"):
                if type(data.get("scope")) == str and 'user:email' in data["scope"]:
                    return {
                        "access_token": data["access_token"],
                        "refresh_token": data.get("refresh_token", None),
                    }
                return "Invalid scope, please try authenticating again"
            else:
                return data.get("error_description", data.get("error", data.get("message",
                                                                                "An unknown error occurred while "
                                                                                "fetching the token from GitHub")))

    @classmethod
    async def get_user_info(cls, access_token: str, refresh_token: str | None):
        async with AsyncClient() as client:
            response = await client.get(f"{cls.api_url}/user", headers={"Authorization": f"token {access_token}"})
            data = response.json()
            if response.status_code != 200:
                return data.get("error_description", data.get("error", data.get("message",
                                                                                "An unknown error occurred while "
                                                                                "fetching user data from GitHub")))
            email_res = await client.get(f"{cls.api_url}/user/emails",
                                         headers={"Authorization": f"token {access_token}"})
            email_data = email_res.json()
            if email_res.status_code != 200:
                return data.get("error_description", data.get("error", data.get("message",
                                                                                "An unknown error occurred while "
                                                                                "fetching email data from GitHub")))
            email = next((email for email in email_data if email.get("primary") and email.get("verified")), None)
            if not email:
                return "No verified primary email found"
            return {
                "provider_id": str(data.get("id")),
                "username": data.get("login"),
                "email": email.get("email"),
                "avatar_url": data.get("avatar_url"),
                "provider": "github"
            }

    @classmethod
    async def revoke_token(cls, access_token: str, refresh_token: str | None):
        async with AsyncClient() as client:
            response = await client.post(f"{cls.api_url}/applications/{cls.client_id}/token",
                                         headers={"Authorization": f"token {access_token}"},
                                         json={"access_token": access_token})
            data = response.json() or dict()
            if response.status_code != 204:
                return data.get("error_description", data.get("error", data.get("message",
                                                                                "An unknown error occurred while "
                                                                                "revoking the token from GitHub")))
            return True


providers = {
    GitHub.name: GitHub
}
