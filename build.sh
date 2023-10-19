#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt

python ca_backend/manage.py collectstatic --no-input
python ca_backend/manage.py migrate