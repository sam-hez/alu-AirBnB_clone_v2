#!/usr/bin/python3
"""Test the user model behavior."""
from tests.test_models.test_base_model import test_basemodel
from models.user import User
from models import storage_t


class test_User(test_basemodel):
    """Check model defaults and inherited behavior."""

    def __init__(self, *args, **kwargs):
        """Select the model class used by these tests."""
        super().__init__(*args, **kwargs)
        self.name = "User"
        self.value = User

    def test_first_name(self):
        """Check first name behavior."""
        new = self.value()
        self.assertEqual(new.first_name,
                         None if storage_t == 'db' else '')

    def test_last_name(self):
        """Check last name behavior."""
        new = self.value()
        self.assertEqual(new.last_name,
                         None if storage_t == 'db' else '')

    def test_email(self):
        """Check email behavior."""
        new = self.value()
        self.assertEqual(new.email,
                         None if storage_t == 'db' else '')

    def test_password(self):
        """Check password behavior."""
        new = self.value()
        self.assertEqual(new.password,
                         None if storage_t == 'db' else '')
