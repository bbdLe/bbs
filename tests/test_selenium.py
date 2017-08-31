from selenium import webdriver
import unittest
import json
from flask import url_for
from app import create_app, db
from base64 import b64encode
from app.models import Role, User, Post, Comment
import re



class SeleniumTestCase(unittest.TestCase):
    client = None

    @classmethod
    def setUpClass(cls):
        try:
            cls.client = webdriver.Firefox()
        except:
            pass
        if cls.client:
            cls.app = create_app("testing")
            cls.app_context = cls.app.app_context()
            cls.app_context.push()

            import logging
            logger = logging.getLogger("werkzeug")
            logger.setLevel("ERROR")

            db.create_all()
            Role.insert_roles()
            User.generate_fake(10)
            Post.generate_fake(10)

            admin_role = Role.query.filter_by(permission=0xff).first()
            admin = User(
                email="john@test.com",
                username="john",
                password="cat",
                role=admin_role,
                confirmed=True
            )
            db.session.add(admin)
            db.session.commit()

            threading.Thread(target=cls.app.run).start()

    @classmethod
    def tearDownClass(cls):
        if cls.client:
            cls.client.get("http://localhost:5000/shutdown")
            cls.client.close()

            db.session.remove()
            db.drop_all()

            cls.app_context.pop()

    def setUp(self):
        if not self.client:
            self.skipTest("Web browser not available")

    def tearDown(self):
        pass

    def test_admin_home_page(self):
        self.client.get("http://localhost:5000/")
        self.assertTrue(re.search("你好", self.client.page_source))
