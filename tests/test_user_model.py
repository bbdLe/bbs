import unittest
from app.models import User, Permission, AnonymousUser, Role
from app import db, create_app
from time import sleep

class UserModelTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app("testing")
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.drop_all()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_password_setter(self):
        u = User(password = "cat")
        self.assertTrue(u.password_hash is not None)

    def test_no_password_getter(self):
        u = User(password="cat")
        with self.assertRaises(AttributeError):
            u.password

    def test_password_verification(self):
        u = User(password="cat")
        self.assertTrue(u.verify_password("cat"))
        self.assertFalse(u.verify_password("dog"))

    def test_password_salts_are_random(self):
        u1 = User(password="cat")
        u2 = User(password="cat")
        self.assertTrue(u1.password_hash != u2.password_hash)

    def test_valid_confirmation_token(self):
        u = User(password="cat")
        db.session.add(u)
        db.session.commit()
        token = u.generate_confirmation_token()
        self.assertTrue(u.confirm(token))
        self.assertTrue(u.confirmed)

    def test_invalid_confirmation_token(self):
        u1 = User(password="cat")
        u2 = User(password="cat")
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()
        token = u1.generate_confirmation_token()
        self.assertFalse(u2.confirm(token))
        self.assertFalse(u2.confirmed)

    def test_expired_confirmation_token(self):
        u = User(password="cat")
        db.session.add(u)
        db.session.commit()
        token = u.generate_confirmation_token(1)
        sleep(3)
        self.assertFalse(u.confirm(token))
        self.assertFalse(u.confirmed)

    def test_valid_reset_password_token(self):
        u = User(password="cat")
        db.session.add(u)
        db.session.commit()
        reset_token = u.gererate_reset_password_token()
        self.assertTrue(u.check_reset_token_and_change_passwd(reset_token, "dog"))
        self.assertTrue(u.verify_password("dog"))

    def test_invalid_reset_password_token(self):
        u1 = User(password="cat")
        u2 = User(password="cat")
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()
        reset_token = u1.gererate_reset_password_token()
        self.assertFalse(u2.check_reset_token_and_change_passwd(reset_token, "dog"))

    def test_expired_reset_password_token(self):
        u = User(password="cat")
        db.session.add(u)
        db.session.commit()
        reset_token = u.gererate_reset_password_token(1)
        sleep(3)
        self.assertFalse(u.check_reset_token_and_change_passwd(reset_token, "dog"))

    def test_roles_and_permissions(self):
        Role.insert_roles()
        u = User(email="test@gmail.com", password="dog")
        self.assertTrue(u.can(Permission.WRITE_ARTICLES))
        self.assertFalse(u.can(Permission.MODERATE_COMMITS))

    def test_anonymous_user(self):
        u = AnonymousUser()
        self.assertFalse(u.can(Permission.WRITE_ARTICLES))
        self.assertFalse(u.can(Permission.COMMENT))
