export MAIL_USERNAME="dalibaxiaoliba19@gmail.com"
export MAIL_PASSWORD="lin8638289"
export C_FORCE_ROOT=1
source /6abbs/venv/bin/activate
celery worker -A celery_runner --loglevel=info&
python /6abbs/manage.py runserver -h 0.0.0.0 -p 80

