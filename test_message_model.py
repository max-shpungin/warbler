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

        m1 = Message.query.get(self.m1_id)

     #   breakpoint()
        self.assertEqual(m1.text, 'test')
        self.assertEqual(m1.user_id, self.u1_id,)


    def test_message_timestamp_exists(self):
        m1 = Message.query.get(self.m1_id)



        self.assertIsInstance(m1.timestamp, datetime)


    def test_message_relationship_user(self):
        """ Test user field can be accessed from related message """
        ...
    def test_message_must_be_created_by_existing_user(self):
        """ message can only be created by an existing user """
        ...

class LikeModelTestCase(TestCase):
    def setUp(self):
        Message.query.delete()
        User.query.delete()

        u1 = User.signup("u1", "u1@email.com", "password", None)
        m1 = Message(text="test", user_id=u1.id)

        db.session.commit()
        self.u1_id = u1.id
        self.m1_id = m1.id

    def tearDown(self):
        db.session.rollback()
