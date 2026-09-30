#!/usr/bin/python3
"""Test the amenity model behavior."""
from tests.test_models.test_base_model import test_basemodel
from models.amenity import Amenity
from models import storage_t


class test_Amenity(test_basemodel):
    """Check model defaults and inherited behavior."""

    def __init__(self, *args, **kwargs):
        """Select the model class used by these tests."""
        super().__init__(*args, **kwargs)
        self.name = "Amenity"
        self.value = Amenity

    def test_name2(self):
        """Check name2 behavior."""
        new = self.value()
        self.assertEqual(new.name,
                         None if storage_t == 'db' else '')
