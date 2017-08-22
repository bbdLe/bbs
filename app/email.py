#-*- coding: utf-8 -*-
from threading import Thread
from flask import current_app, render_template
from flask_mail import Message
from . import mail
from .extensions import flask_celery
from time import sleep

# def send_sync_mail(msg):
#     with app.app_context():
#     mail.send(msg)
#app = create_app("default")

@flask_celery.task()
def send_async_email(msg):
    mail.send(msg)

# @celery.task()
# def add(a, b):
#     return a + b

def send_mail(to, subject, template, **kwargs):
    app = current_app._get_current_object()
    msg = Message(app.config["BBS_MAIL_SENDER"] + subject,
                  sender=app.config["BBS_MAIL_SENDER"],
                  recipients=[to])
    msg.body = render_template(template + ".txt", **kwargs)
    #add.delay(1, 2)
    send_async_email.delay(msg)
