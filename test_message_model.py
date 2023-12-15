"""Message model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase
from datetime import datetime

from models import db, User, Message, Like
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

class MessageModelTestCase(TestCase):
    def setUp(self):
        Message.query.delete()
        User.query.delete()

        u1 = User.signup("u1", "u1@email.com", "password", None)
        db.session.commit()

       # breakpoint()

        m1 = Message(text="test", user_id=u1.id)
        db.session.add(m1)

        db.session.commit()
        self.u1_id = u1.id
        self.m1_id = m1.id

    def tearDown(self):
        db.session.rollback()

    def test_message_model(self):
        """Tests that Message is created"""

        m1 = Message.query.get(self.m1_id)

        self.assertEqual(m1.text, 'test')
        self.assertEqual(m1.user_id, self.u1_id,)


    def test_message_timestamp_exists(self):
        """
        Tests that timestamp is created by default and is a datetime
        """

        m1 = Message.query.get(self.m1_id)
        self.assertIsInstance(m1.timestamp, datetime)


    def test_message_relationship_user(self):
        """ Test user field can be accessed from related message """

        m1 = Message.query.get(self.m1_id)

        self.assertTrue(m1.user.password)

    def test_message_must_be_created_by_existing_user(self):
        """ message can only be created by an existing user """

        with self.assertRaises(IntegrityError):
            m2 = Message(text="test", user_id = 0)
            db.session.add(m2)
            db.session.commit()


class LikeModelTestCase(TestCase):
    def setUp(self):
        Message.query.delete()
        User.query.delete()

        u1 = User.signup("u1", "u1@email.com", "password", None)
        u2 = User.signup("u2", "u2@email.com", "password", None)

        db.session.commit()

        m1 = Message(text="test", user_id=u1.id)
        m2 = Message(text="test2", user_id=u2.id)

        db.session.add(m1)
        db.session.add(m2)
        db.session.commit()
        self.u1_id = u1.id
        self.u2_id = u2.id
        self.m1_id = m1.id
        self.m2_id = m2.id

    def tearDown(self):
        db.session.rollback()

    def test_can_like_others_messages(self):
        """Tests that user can like messages they didn't write"""

        u1 = User.query.get(self.u1_id)
        m2 = Message.query.get(self.m2_id)

        u1.liked_messages.append(m2)
        db.session.commit()

        self.assertEqual(len(u1.liked_messages), 1)

    def test_can_unlike(self):
        """Tests that user can unlike messages they didn't write"""

        u1 = User.query.get(self.u1_id)
        m2 = Message.query.get(self.m2_id)

        u1.liked_messages.append(m2)
        db.session.commit()

        u1.liked_messages.remove(m2)
        db.session.commit()

        self.assertEqual(len(u1.liked_messages), 0)