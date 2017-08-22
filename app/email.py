#-*- coding: utf-8 -*-
from threading import Thread
from flask import current_app, render_template
from flask_mail import Message
from . import mail, celery
#from .. import app 互相import会报错，因为app会调用email
#from celery import Celery

#celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
#celery.conf.update(app.config)

def send_sync_mail(app, msg):
    with app.app_context():
        mail.send(msg)

@celery.task
def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)

def send_mail(to, subject, template, **kwargs):
    app = current_app._get_current_object()
    msg = Message(app.config["BBS_MAIL_SENDER"] + subject,
                  sender=app.config["BBS_MAIL_SENDER"],
                  recipients=[to])
    msg.body = render_template(template + ".txt", **kwargs)
    send_async_email(app, msg)
