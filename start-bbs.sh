export MAIL_USERNAME=""
export MAIL_PASSWORD=""
export C_FORCE_ROOT=1
source /6abbs/venv/bin/activate
celery worker -A celery_runner --loglevel=info &
python /6abbs/manage.py runserver -h 0.0.0.0 -p 80
