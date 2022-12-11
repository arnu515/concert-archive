FROM node:18-alpine as frontend

WORKDIR /app

RUN npm i -g pnpm

COPY ./frontend/package.json ./
COPY ./frontend/pnpm_lock.yaml ./

RUN pnpm i

COPY frontend .

RUN pnpm build

FROM python:3.11-slim as runner

RUN apt install build-essential

RUN pip install --upgrade pip

RUN curl https://install.python-poetry.org | POETRY_HOME=/opt/poetry python3 -

ENV PATH="/opt/poetry/bin:${PATH}"

WORKDIR /app

COPY ./backend/pyproject.toml ./
COPY ./backend/poetry.lock ./

RUN poetry install --no-dev

COPY ./backend .
COPY --from=frontend /app/build ./static

RUN prisma generate

EXPOSE 5000

CMD ["python", "main.py"]
