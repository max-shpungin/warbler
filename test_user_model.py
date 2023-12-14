"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase

from models import db, User, Message, Follow, DEFAULT_IMAGE_URL,DEFAULT_HEADER_IMAGE_URL
from sqlalchemy.exc import IntegrityError

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler_test"

# Now we can import app

from app import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

# Make Flask errors be real errors, rather than HTML pages with error info
app.config['TESTING'] = True

# This is a bit of hack, but don't use Flask DebugToolbar
app.config['DEBUG_TB_HOSTS'] = ['dont-show-debug-toolbar']

db.drop_all()
db.create_all()


class UserModelTestCase(TestCase):
    def setUp(self):
        User.query.delete()

        u1 = User.signup("u1", "u1@email.com", "password", None)
        u2 = User.signup("u2", "u2@email.com", "password", None)

        db.session.commit()
        self.u1_id = u1.id
        self.u2_id = u2.id

    def tearDown(self):
        db.session.rollback()

    def test_user_model(self):
        u1 = User.query.get(self.u1_id)

        # User should have no messages & no followers
        self.assertEqual(len(u1.messages), 0)
        self.assertEqual(len(u1.followers), 0)

    def test_signup_positive(self):
        """
        Tests that signup method successfully creates a user given
        valid credentials
        """

        u3 = User.signup(
            "tuckerdiane",
            "tuckerdiane@example.org",
            "password",
            None
        )
        db.session.commit()

        self.assertTrue(u3)

    def test_signup_negative_no_password(self):
        """
        Tests that signup method raises an error given no password
        """

        with self.assertRaises(ValueError):
            u3 = User.signup("u3", "u3@email.com", None, None)

    def test_signup_negative_no_email(self):
        """Tests that signup method raises an error given no email and does not
        create a user"""

        with self.assertRaises(IntegrityError):
            u3 = User.signup("u3", None, "password", None)
            db.session.commit()

    def test_signup_negative_dupe(self):
        """
        Checks that a user signing up with an already in use username will
        raise an error
        """

        with self.assertRaises(IntegrityError):
            u3 = User.signup("u1", "u45@email.com", "passwordabc", None)
            db.session.commit()


    def test_default_values(self):
        """
        Ensures that the test user was assigned the default values for the
        fields that were entered as None
        """

        test_user = User.query.get(self.u1_id)
        self.assertEqual(test_user.image_url, DEFAULT_IMAGE_URL)
        self.assertEqual(test_user.header_image_url, DEFAULT_HEADER_IMAGE_URL)
        self.assertEqual(test_user.bio, "")
        self.assertEqual(test_user.location, "")


    def test_is_following_positive(self):
        """
        Ensures that is_following returns True when a user is following another
        """
        #someone needs to follow someone

        test_user_1 = User.query.get(self.u1_id)
        test_user_2 = User.query.get(self.u2_id)

        test_user_1.following.append(test_user_2)
        db.session.commit()

        self.assertTrue(test_user_1.is_following(test_user_2))

    def test_is_following_negative(self):
        """
        Ensures that is_following returns False when a user is not following
        another
        """

        test_user_1 = User.query.get(self.u1_id)
        test_user_2 = User.query.get(self.u2_id)

        self.assertFalse(test_user_1.is_following(test_user_2))

    def test_is_followed_by_positive(self):
        """
        Ensures that is_followed_by returns True when a user is followed by
        another
        """

        test_user_1 = User.query.get(self.u1_id)
        test_user_2 = User.query.get(self.u2_id)

        test_user_1.following.append(test_user_2)
        db.session.commit()

        self.assertTrue(test_user_2.is_followed_by(test_user_1))

    def test_is_followed_by_negative(self):
        """
        Ensures that is_followed_by returns False when a user is not followed
        by another
        """

        test_user_1 = User.query.get(self.u1_id)
        test_user_2 = User.query.get(self.u2_id)

        self.assertFalse(test_user_1.is_followed_by(test_user_2))


    def test_authenticate_positive(self):
        """
        Ensures that authenticate returns True when given the correct
        credentials
        """

        test_user_1 = User.query.get(self.u1_id)

        self.assertEqual(
            test_user_1,
            User.authenticate(test_user_1.username, test_user_1.password)
        )

    def test_authenticate_negative_wrong_password(self):
        """
        Ensures that authenticate returns False when given the incorrect
        password
        """

        test_user_1 = User.query.get(self.u1_id)

        self.assertFalse(User.authenticate(test_user_1.username, "asedfghklaf"))

    def test_authenticate_negative_wrong_username(self):
        """
        Ensures that authenticate returns False when given the incorrect
        username
        """

        test_user_1 = User.query.get(self.u1_id)

        bad_username = test_user_1.username + "s"

        self.assertFalse(User.authenticate(bad_username, test_user_1.password))
