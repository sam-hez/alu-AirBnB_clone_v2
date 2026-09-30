#!/usr/bin/python3
"""Test the review model behavior."""
from tests.test_models.test_base_model import test_basemodel
from models.review import Review
from models import storage_t


class test_review(test_basemodel):
    """Check model defaults and inherited behavior."""

    def __init__(self, *args, **kwargs):
        """Select the model class used by these tests."""
        super().__init__(*args, **kwargs)
        self.name = "Review"
        self.value = Review

    def test_place_id(self):
        """Check place id behavior."""
        new = self.value()
        self.assertEqual(new.place_id,
                         None if storage_t == 'db' else '')

    def test_user_id(self):
        """Check user id behavior."""
        new = self.value()
        self.assertEqual(new.user_id,
                         None if storage_t == 'db' else '')

    def test_text(self):
        """Check text behavior."""
        new = self.value()
        self.assertEqual(new.text,
                         None if storage_t == 'db' else '')
