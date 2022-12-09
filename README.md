# [Concert](https://concert.arnu515.me)

Source code for my project made for the [MongoDB Atlas Hackathon 2022 on DEV](https://dev.to/devteam/announcing-the-mongodb-atlas-hackathon-2022-on-dev-2107).

Will be hosted live until Jan 1 2022.
Hosted live at: https://concert.arnu515.me

## Prerequisites

- Python3.11 with the [Poetry](https://python-poetry.org) package manager installed.
- NodeJS 18 LTS with the [pnpm](https://pnpm.io) package manager installed.
- The [Livekit SFU server binary](https://github.com/livekit/livekit/releases/tag/v1.3.1) downloaded on your computer.
- A MongoDB database. You can host one on [MongoDB Atlas](https://cloud.mongodb.com) for free.
- A [GitHub](https://github.com/settings/developers) and [GitLab](https://gitlab.com/-/profile/applications) OAuth app.

## Get started

1. Clone the repository to an empty folder

2. Install dependenices

```bash
cd frontend
pnpm install
cd ..

cd backend
poetry install
cd ..
```

3. Copy the `.env.example` file to `.env` and symlink/copy it to the frontend and backend folders

```bash
cp .env.example .env
ln -sf .env backend/.env
ln -sf .env frontend/.env
```

4. Edit the `.env` file and replace the example variables with your values.

5. Run the servers in three terminals

```bash
# Terminal 1 - Livekit
path/to/livekit-server --dev  # http://localhost:7880

# Terminal 2 - Backend
cd backend
poetry run python3 main.py  # http://localhost:5000

# Terminal 3 - Frontend
cd frontend
pnpm dev  # http://localhost:3000
```
