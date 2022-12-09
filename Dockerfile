# Get doppler env
FROM alpine:3.17.0 AS doppler

# Whether to use doppler for secrets
ARG USE_DOPPLER="false"

# If the above option is true, you need to pass in these variables
ARG DOPPLER_TOKEN=""
ARG DOPPLER_PROJECT=""
ARG DOPPLER_CONFIG=""

RUN mkdir /app /app/frontend
WORKDIR /app

# INSTALL DOPPLER
RUN if [ "$USE_DOPPLER" = "true" ] ; then \
    apk add --no-cache wget gnupg && wget -t 3 -qO- https://cli.doppler.com/install.sh | sh; \
    fi

# Download the doppler environment variables
RUN if [ "$USE_DOPPLER" = "true" ] ; then \
    doppler configure set token $DOPPLER_TOKEN --scope / && \
    doppler secrets download --project $DOPPLER_PROJECT --config $DOPPLER_CONFIG --format env --no-file > .env; \
    fi

# BUILDING FRONTEND
FROM node:18-alpine AS frontend

RUN mkdir /app
WORKDIR /app

# Install pnpm
RUN npm install -g pnpm

# Copy .env
COPY --from=doppler /app/.env .

# Copy packager files
COPY ./frontend/package.json .
COPY ./frontend/pnpm-lock.yaml .

# Install frontend dependencies
RUN pnpm i

# Copy the rest of the files
COPY ./frontend .

# Build the app
RUN pnpm build

# RUNNING BACKEND
FROM python:3.11-slim AS backend

RUN mkdir /app
WORKDIR /app

COPY ./backend/pyproject.toml .
COPY ./backend/poetry.lock .

# Install poetry
RUN apt-get update -y && apt-get -y install build-essential make g++ libffi-dev && pip install poetry

# Install backend dependencies
RUN poetry install

# Copy the rest of the files
COPY ./backend .

# Install a special version of prisma
# RUN /venv/bin/pip uninstall prisma -y && /venv/bin/pip install git+https://github.com/RobertCraigie/prisma-client-py@refactor/remove-pkg-cli

# Add venv to path. Required for prisma to work properly
#RUN export OLD_PATH=$PATH && export PATH="/venv/bin:$PATH" && \
#    # Fetch prisma binaries \
#    prisma py fetch && \
#    # Generate prisma client \
#    prisma py generate --schema ./prisma/schema.prisma && \
#    # Build \
#    /venv/bin/poetry build && /venv/bin/pip install dist/*.whl && \
#    # Restore path \
#    export PATH=$OLD_PATH

# Copy required files from builders
COPY --from=doppler /app/.env .
COPY --from=frontend /app/build ./static

RUN poetry run prisma py generate

# Run the app
CMD ["poetry", "run", "python3", "main.py"]
