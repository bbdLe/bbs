import os
from celery import Celery
from app import create_app

def make_celery(app):
    """Create the celery process."""

    # Init the celery object via app's configuration.
    celery = Celery(
        app.import_name,
        backend=app.config['CELERY_RESULT_BACKEND'],
        broker=app.config['CELERY_BROKER_URL'])

    # Flask-Celery-Helpwe to auto-setup the config.
    celery.conf.update(app.config)
    TaskBase = celery.Task

    class ContextTask(TaskBase):

        abstract = True

        def __call__(self, *args, **kwargs):
            """Will be execute when create the instance object of ContextTesk.
            """

            # Will context(Flask's Extends) of app object(Producer Sit)
            # be included in celery object(Consumer Site).
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)

    # Include the app_context into celery.Task.
    # Let other Flask extensions can be normal calls.
    celery.Task = ContextTask
    return celery

config = os.environ.get('BBS_CONFIG', 'development')
flask_app = create_app(config)
celery = make_celery(flask_app)