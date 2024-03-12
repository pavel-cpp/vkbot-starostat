CUR_DIR=$(shell pwd)
VERSION_ENV=$(shell grep ^VERSION= .env | cut -d "=" -f 2-)
VERSION = $(shell echo $${VERSION:-$(VERSION_ENV)})
COMPOSE_PROJECT_NAME_ENV=$(shell grep ^COMPOSE_PROJECT_NAME= .env | cut -d "=" -f 2-)
COMPOSE_PROJECT_NAME = $(shell echo $${COMPOSE_PROJECT_NAME:-$(COMPOSE_PROJECT_NAME_ENV)})

##
# Backend
##

build:
	docker compose -f docker-compose.yml -f docker-compose.dev.yml build ${SERVICE}

up:
	docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d

down:
	docker compose -f docker-compose.yml -f docker-compose.dev.yml down

##
# Packages
##

poetry_install:
	docker compose -f docker-compose.yml -f docker-compose.dev.yml run --no-deps backend poetry install

poetry_lock:
	docker compose -f docker-compose.yml -f docker-compose.dev.yml run --no-deps backend poetry lock --no-update

poetry_add:
	docker compose -f docker-compose.yml -f docker-compose.dev.yml run --no-deps backend poetry add ${PACKAGE}

##
# Tests
##


mypy:
	docker run -e ENVIRONMENT=test -v ${CUR_DIR}/src:/app --rm ${COMPOSE_PROJECT_NAME}/fastapi:${VERSION}-dev make mypy

linter:
	docker run -e ENVIRONMENT=test -v ${CUR_DIR}/src:/app --rm ${COMPOSE_PROJECT_NAME}/fastapi:${VERSION}-dev make ltest

pytest:
	docker run -e PYTHONPATH=/app -e ENVIRONMENT=test -v ${CUR_DIR}/src:/app --rm ${COMPOSE_PROJECT_NAME}/fastapi:${VERSION}-dev make pytest

ltest: mypy linter
