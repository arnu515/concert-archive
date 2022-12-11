
FROM node:18-alpine as frontend

WORKDIR /app

RUN npm i -g pnpm

COPY ./frontend/package.json ./
COPY ./frontend/pnpm-lock.yaml ./

RUN pnpm i

# change as required
ENV PUBLIC_LIVEKIT_URL="https://concert.arnu515.me"

COPY frontend .
RUN pnpm build

FROM python:3.11-slim as runner

RUN apt-get -y update && \
  # install python deps
  apt-get -y install curl libffi-dev libpq-dev gcc make

RUN pip install --upgrade pip

RUN curl https://install.python-poetry.org | POETRY_HOME=/opt/poetry python3 -

ENV PATH="/opt/poetry/bin:${PATH}"

WORKDIR /app

COPY ./backend/pyproject.toml ./
COPY ./backend/poetry.lock ./

RUN poetry install --no-dev

COPY ./backend .
COPY --from=frontend /app/build ./static

RUN poetry run prisma generate

EXPOSE 5000

CMD ["python", "main.py"]
