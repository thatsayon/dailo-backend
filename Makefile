run:
	python manage.py runserver

migrate:
	python manage.py makemigrations
	python manage.py migrate

superuser:
	python manage.py createsuperuser

collectstatic:
	python manage.py collectstatic --noinput

docker-up:
	docker-compose up --build

docker-down:
	docker-compose down
