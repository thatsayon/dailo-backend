.PHONY: run migrate superuser collectstatic docker-up docker-down sync venv

# create virtual env (if not created)
venv:
	uv venv

# install dependencies from lock file
sync:
	uv sync

# run django server
run:
	uv run python manage.py runserver

# migrations
migrate:
	uv run python manage.py makemigrations
	uv run python manage.py migrate

# create admin user
superuser:
	uv run python manage.py createsuperuser

# collect static files
collectstatic:
	uv run python manage.py collectstatic --noinput

# docker
docker-up:
	docker-compose up --build

docker-down:
	docker-compose down
