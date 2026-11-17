#!/usr/bin/env bash
set -euo pipefail
# Free plans have no pre-deploy command. One web instance runs release tasks here.
python manage.py migrate --noinput
python manage.py setup_roles
python manage.py bootstrap_admin
if [ "${SEED_DEMO:-0}" = "1" ]; then python manage.py seed_demo; fi
exec gunicorn config.wsgi:application --bind "0.0.0.0:${PORT:-10000}" --workers 2 --timeout 60 --access-logfile -
