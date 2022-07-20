#!/bin/sh

python manage.py makemigrations
python manage.py migrate
#python manage.py loadcsv
python manage.py collectstatic --noinput

exec "$@"