"""Message View tests."""

# run these tests like:
#
#    FLASK_DEBUG=False python -m unittest test_message_views.py


import os
from unittest import TestCase

from models import db, Message, User

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler_test"

# Now we can import app

from app import app, CURR_USER_KEY

app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

# This is a bit of hack, but don't use Flask DebugToolbar

app.config['DEBUG_TB_HOSTS'] = ['dont-show-debug-toolbar']

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.drop_all()
db.create_all()

# Don't have WTForms use CSRF at all, since it's a pain to test

app.config['WTF_CSRF_ENABLED'] = False


class MessageBaseViewTestCase(TestCase):
    def setUp(self):
        User.query.delete()

        u1 = User.signup("u1", "u1@email.com", "password", None)
        db.session.flush()

        m1 = Message(text="m1-text", user_id=u1.id)
        db.session.add_all([m1])
        db.session.commit()

        self.u1_id = u1.id
        self.m1_id = m1.id

class MessageAddViewTestCase(MessageBaseViewTestCase):
    def test_add_message(self):
        # Since we need to change the session to mimic logging in,
        # we need to use the changing-session trick:
        with app.test_client() as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1_id

            # Now, that session setting is saved, so we can have
            # the rest of ours test
            resp = c.post("/messages/new", data={"text": "Hello"})

            self.assertEqual(resp.status_code, 302)

            Message.query.filter_by(text="Hello").one()

    def test_delete_message(self):
        """Test that user can delete a message they wrote"""

        with app.test_client() as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1_id

            resp = c.post(f'/messages/{self.m1_id}/delete')

            self.assertEqual(resp.status_code, 302)

            self.assertIsNone(Message.query
                              .filter_by(id=self.m1_id)
                              .one_or_none())

    def test_cant_delete_others_messages(self):
        """Test that users can't delete messages they didn't write"""

        with app.test_client() as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1_id

            resp = c.post(f'/messages/{self.m2_id}/delete',
                          follow_redirects=True)

            self.assertEqual(resp.status_code, 200)

            html = resp.get_data(as_text=True)

            self.assertIn("Access unauthorized.", html)

            self.assertIsNotNone(Message.query
                              .filter_by(id=self.m2_id)
                              .one_or_none())

    def test_show_message(self):
        """Test that a message displays"""

        with app.test_client() as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1_id

            resp = c.get(f'/messages/{self.m1_id}')
            self.assertEqual(resp.status_code, 200)

            message = Message.query.get(self.m1_id)

            html = resp.get_data(as_text=True)
            self.assertIn(f"{message.text}", html)

    def test_show_invalid_message(self):
        """Check that messages that don't exist don't display"""

        with app.test_client() as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1_id

            resp = c.get(f'/messages/0')
            self.assertEqual(resp.status_code, 404)