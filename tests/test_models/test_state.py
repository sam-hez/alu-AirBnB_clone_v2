#!/usr/bin/python3
"""Test the state model behavior."""
from tests.test_models.test_base_model import test_basemodel
from models.state import State
from models.city import City
from models import storage, storage_t
import unittest


class test_state(test_basemodel):
    """Check model defaults and inherited behavior."""

    def __init__(self, *args, **kwargs):
        """Select the model class used by these tests."""
        super().__init__(*args, **kwargs)
        self.name = "State"
        self.value = State

    def test_name3(self):
        """Check name3 behavior."""
        new = self.value()
        self.assertEqual(new.name, None if storage_t == 'db' else '')

    @unittest.skipIf(storage_t == 'db', 'Tests the file storage getter.')
    def test_cities(self):
        """Return only saved cities belonging to this state."""
        state = State(name='California')
        other = State(name='Nevada')
        self.assertEqual(state.cities, [])
        city = City(name='Oakland', state_id=state.id)
        self.assertEqual(state.cities, [])
        city.save()
        unrelated = City(name='Reno', state_id=other.id)
        unrelated.save()
        self.assertEqual(state.cities, [city])
        city.state_id = other.id
        self.assertEqual(state.cities, [])
        self.assertCountEqual(other.cities, [city, unrelated])
        unrelated.delete()
        self.assertEqual(other.cities, [city])
        with self.assertRaises(AttributeError):
            state.cities = []
