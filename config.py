#-*- coding: utf-8 -*-

import os
import logging
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or "hard to guess string"
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    BBS_MAIl_SUBJECT_PREFIX = "[论坛]"
    BBS_MAIL_SENDER = "论坛管理员 <dalibaxiaoliba19@gmail.com>"
    BBS_ADMIN = os.environ.get("BBS_ADMIN")
    CELERY_BROKER_URL = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND = "redis://localhost:6379/0"
    SQLALCHEMY_RECORD_QUERY = True

    @staticmethod
    def init_app(app):
        pass

class DevelopmentConfig(Config):
    DEBUG = True
    MAIL_SERVER = "smtp.gmail.com"
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")
    SQLALCHEMY_DATABASE_URI = "mysql://root:b77681335@localhost/dev"

    def init_app(app):
        handler = logging.FileHandler('flask2.log', encoding='UTF-8')
        handler.setLevel(logging.WARNING)
        logging_format = logging.Formatter('%(asctime)s - %(levelname)s - %(filename)s - %(funcName)s - %(lineno)s - %(message)s')
        handler.setFormatter(logging_format)
        app.logger.addHandler(handler)

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "mysql://root:b77681335@localhost/test"
    WTF_CSRF_ENABLED = False

config = {
    'development': DevelopmentConfig,
    'default': DevelopmentConfig,
    'testing': TestingConfig
}
