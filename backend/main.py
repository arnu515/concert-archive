import os

from dotenv import load_dotenv

from concert_backend import app

load_dotenv()

if __name__ == "__main__":
    app.run(host=os.getenv("HOST", "0.0.0.0"), port=int(os.getenv("PORT", 5000)), debug=True, auto_reload=True,
            access_log=bool(int(os.getenv("DEV"))), motd=bool(int(os.getenv("DEV"))),
            fast=not bool(int(os.getenv("DEV"))))
