run-api:
	uv run uvicorn correspondence.main:app --reload --log-config uvicorn_disable_logging.json

run-worker:
	uv run taskiq worker correspondence.broker:broker

dropdb:
	dropdb --if-exists correspondence

createdb:
	createdb -E utf-8 correspondence

lint:
	uv run ruff check correspondence/ tests/

check:
	uv run mypy correspondence tests --check-untyped-defs

safe: fmt lint check

shell:
	uv run python -m correspondence.cli shell

fmt:
	uv run ruff format correspondence/ tests/
	uv run isort correspondence/ tests/

migrate:
	uv run alembic -c alembic.ini upgrade head

flush: dropdb createdb migrate

run-test:
	CORRESPONDENCE_API_ENV=testing uv run pytest tests/ -vs

rebuilddb:
	dropdb --if-exists correspondence_test
	createdb -E utf-8 correspondence_test
	CORRESPONDENCE_API_ENV=testing uv run alembic -c alembic.ini upgrade head

test: rebuilddb run-test

ci:
	CORRESPONDENCE_API_ENV=testing uv run alembic -c alembic.ini upgrade head
	CORRESPONDENCE_API_ENV=testing uv run pytest tests/ -vs

outdated:
	bash -c "uv pip list --format=freeze |sed 's/==.*//' | uv pip compile - --no-deps --no-header |diff <(uv pip list --format=freeze) - -y --suppress-common-lines || :"
