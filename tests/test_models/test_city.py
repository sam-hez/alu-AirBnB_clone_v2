#!/usr/bin/python3
"""Test the city model behavior."""
from tests.test_models.test_base_model import test_basemodel
from models.city import City
from models import storage_t


class test_City(test_basemodel):
    """Check model defaults and inherited behavior."""

    def __init__(self, *args, **kwargs):
        """Select the model class used by these tests."""
        super().__init__(*args, **kwargs)
        self.name = "City"
        self.value = City

    def test_state_id(self):
        """Check state id behavior."""
        new = self.value()
        self.assertEqual(new.state_id, None if storage_t == 'db' else '')

    def test_name(self):
        """Check name behavior."""
        new = self.value()
        self.assertEqual(new.name, None if storage_t == 'db' else '')
