#!/bin/bash
pip3 install pipenv
pipenv install
pipenv run python3.11 manage.py collectstatic --noinput
pipenv run python3.11 manage.py migrate
pipenv run gunicorn --workers 2 shorthub.wsgi --log-file -
