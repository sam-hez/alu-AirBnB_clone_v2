#!/usr/bin/python3
"""Test the place model behavior."""
from tests.test_models.test_base_model import test_basemodel
from models.place import Place
from models import storage_t


class test_Place(test_basemodel):
    """Check model defaults and inherited behavior."""

    def __init__(self, *args, **kwargs):
        """Select the model class used by these tests."""
        super().__init__(*args, **kwargs)
        self.name = "Place"
        self.value = Place

    def test_city_id(self):
        """Check city id behavior."""
        new = self.value()
        self.assertEqual(new.city_id,
                         None if storage_t == 'db' else '')

    def test_user_id(self):
        """Check user id behavior."""
        new = self.value()
        self.assertEqual(new.user_id,
                         None if storage_t == 'db' else '')

    def test_name(self):
        """Check name behavior."""
        new = self.value()
        self.assertEqual(new.name,
                         None if storage_t == 'db' else '')

    def test_description(self):
        """Check description behavior."""
        new = self.value()
        self.assertEqual(new.description,
                         None if storage_t == 'db' else '')

    def test_number_rooms(self):
        """Check number rooms behavior."""
        new = self.value()
        self.assertEqual(type(new.number_rooms), int)

    def test_number_bathrooms(self):
        """Check number bathrooms behavior."""
        new = self.value()
        self.assertEqual(type(new.number_bathrooms), int)

    def test_max_guest(self):
        """Check max guest behavior."""
        new = self.value()
        self.assertEqual(type(new.max_guest), int)

    def test_price_by_night(self):
        """Check price by night behavior."""
        new = self.value()
        self.assertEqual(type(new.price_by_night), int)

    def test_latitude(self):
        """Check latitude behavior."""
        new = self.value()
        self.assertEqual(new.latitude,
                         None if storage_t == 'db' else 0.0)

    def test_longitude(self):
        """Check longitude behavior."""
        new = self.value()
        self.assertEqual(new.longitude,
                         None if storage_t == 'db' else 0.0)

    def test_amenity_ids(self):
        """Check amenity ids behavior."""
        new = self.value()
        self.assertEqual(type(new.amenity_ids), list)
