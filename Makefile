run-api:
	uv run uvicorn correspondence.main:app --reload --log-config uvicorn_disable_logging.json

run-worker:
	uv run taskiq worker correspondence.broker:broker

dropdb:
	dropdb --if-exists escalidraw

createdb:
	createdb -E utf-8 escalidraw

lint:
	uv run ruff check correspondence/ tests/

check:
	uv run mypy correspondence tests --check-untyped-defs

shell:
	uv run ipython

fmt:
	uv run ruff format correspondence/ tests/
	uv run isort correspondence/ tests/

migrate:
	uv run alembic -c alembic.ini upgrade head

flush: dropdb createdb migrate

run-test:
	CORRESPONDENCE_API_ENV=testing uv run pytest tests/ -vs

rebuilddb:
	dropdb --if-exists escalidraw_test
	createdb -E utf-8 escalidraw_test
	CORRESPONDENCE_API_ENV=testing uv run alembic -c alembic.ini upgrade head

test: rebuilddb run-test

ci:
	CORRESPONDENCE_API_ENV=testing uv run alembic -c alembic.ini upgrade head
	CORRESPONDENCE_API_ENV=testing uv run pytest tests/ -vs
