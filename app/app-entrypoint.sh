#!/bin/sh

if [ "$DATABASE" = "postgres" ]
then
    echo "Waiting for postgres..."

    while ! nc -z $APP_SQL_HOST $APP_SQL_PORT; do
      sleep 0.1
    done

    echo "PostgreSQL started"
fi
python manage.py migrate
python manage.py collectstatic --no-input --clear
exec "$@"