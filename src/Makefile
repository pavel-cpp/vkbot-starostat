###
# Run
###

run_dev:
	uvicorn main:app --host 0.0.0.0 --port 8000 --reload

run_prod:
	uvicorn main:app --host 0.0.0.0 --port 8000 --log-level warning

###
# Migrations
###

migrations:
	alembic revision --autogenerate

upgrade:
	alembic upgrade head

###
# Linter Tests
###

radon:
	poetry run radon mi -s -n B .

flake:
	poetry run flake8

bandit:
	poetry run bandit -c configs/bandit.yaml -r app

mypy:
	poetry run mypy .

isort:
	poetry run isort .
isort_ci:
	poetry run isort --check-only .

black:
	poetry run black .
black_ci:
	poetry run black --check .

ltest: black isort flake bandit radon
ltest_ci: black_ci isort_ci flake bandit radon

###
# Unit Tests
###

pytest:
	python -m pytest -c configs/pytest.ini app/
