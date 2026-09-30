#!/usr/bin/python3
"""Test the review model behavior."""
from tests.test_models.test_base_model import test_basemodel
from models.review import Review


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
        self.assertEqual(type(new.place_id), str)

    def test_user_id(self):
        """Check user id behavior."""
        new = self.value()
        self.assertEqual(type(new.user_id), str)

    def test_text(self):
        """Check text behavior."""
        new = self.value()
        self.assertEqual(type(new.text), str)
