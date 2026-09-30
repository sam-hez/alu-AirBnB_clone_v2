#!/usr/bin/python3
"""Verify every mapped model with independent SQL queries."""
import unittest
from datetime import datetime
from models import storage, storage_t
from tests.test_db_support import DatabaseFixture


class ModelChecks(DatabaseFixture):
    """Share meaningful persistence checks across all six models."""

    def test_saved_row(self):
        """Saving creates a row with the expected primary key."""
        obj = self.objects[self.model]
        count = self.sql_value('SELECT COUNT(*) FROM ' + obj.__tablename__
                               + ' WHERE id = %s', (obj.id,))
        self.assertEqual(count, 1)

    def test_serialized_attributes(self):
        """Serialization includes the class but excludes ORM internals."""
        obj = self.objects[self.model]
        data = obj.to_dict()
        self.assertEqual(data['__class__'], self.model)
        self.assertNotIn('_sa_instance_state', data)
        self.assertIsInstance(data['created_at'], str)

    def test_dictionary_reconstruction(self):
        """Serialized dictionaries rebuild an independent model instance."""
        obj = self.objects[self.model]
        restored = type(obj)(**obj.to_dict())
        self.assertEqual(restored.to_dict(), obj.to_dict())
        self.assertIsNot(restored, obj)

    def test_update_persisted(self):
        """Attribute assignment produces an UPDATE visible in MySQL."""
        obj = self.objects[self.model]
        setattr(obj, self.field, 'Updated value')
        obj.save()
        value = self.sql_value('SELECT ' + self.field + ' FROM '
                               + obj.__tablename__ + ' WHERE id = %s',
                               (obj.id,))
        self.assertEqual(value, 'Updated value')

    def test_delete_persisted(self):
        """Deleting a model removes its row after commit."""
        original = self.objects[self.model]
        data = original.to_dict()
        for field in ('id', '__class__', 'created_at', 'updated_at'):
            data.pop(field)
        obj = type(original)(**data)
        obj.save()
        obj.delete()
        storage.save()
        count = self.sql_value('SELECT COUNT(*) FROM ' + obj.__tablename__
                               + ' WHERE id = %s', (obj.id,))
        self.assertEqual(count, 0)

    def test_filter_class(self):
        """Class filters return only instances of the requested model."""
        obj = self.objects[self.model]
        self.assertEqual(list(storage.all(type(obj))),
                         [self.model + '.' + obj.id])

    def test_filter_name(self):
        """String class names select the same database rows."""
        obj = self.objects[self.model]
        self.assertEqual(list(storage.all(self.model)),
                         [self.model + '.' + obj.id])

    def test_timestamps(self):
        """Loaded models preserve datetime timestamps and creation time."""
        obj = self.objects[self.model]
        created = obj.created_at
        obj.updated_at = datetime(2000, 1, 1)
        obj.save()
        self.assertEqual(obj.created_at, created)
        self.assertGreater(obj.updated_at, datetime(2000, 1, 1))

    def test_reload(self):
        """Closing the session leaves committed model fields intact."""
        obj = self.objects[self.model]
        storage.close()
        restored = storage.all(self.model)[self.model + '.' + obj.id]
        self.assertEqual(getattr(restored, self.field),
                         getattr(obj, self.field))
        self.assertIsNot(restored, obj)


@unittest.skipIf(storage_t != 'db', 'Requires database storage.')
class TestDBUser(ModelChecks, unittest.TestCase):
    """Check user persistence."""
    model = 'User'
    field = 'first_name'


@unittest.skipIf(storage_t != 'db', 'Requires database storage.')
class TestDBState(ModelChecks, unittest.TestCase):
    """Check state persistence."""
    model = 'State'
    field = 'name'


@unittest.skipIf(storage_t != 'db', 'Requires database storage.')
class TestDBCity(ModelChecks, unittest.TestCase):
    """Check city persistence and state references."""
    model = 'City'
    field = 'name'


@unittest.skipIf(storage_t != 'db', 'Requires database storage.')
class TestDBAmenity(ModelChecks, unittest.TestCase):
    """Check amenity persistence."""
    model = 'Amenity'
    field = 'name'


@unittest.skipIf(storage_t != 'db', 'Requires database storage.')
class TestDBPlace(ModelChecks, unittest.TestCase):
    """Check place persistence and foreign keys."""
    model = 'Place'
    field = 'description'


@unittest.skipIf(storage_t != 'db', 'Requires database storage.')
class TestDBReview(ModelChecks, unittest.TestCase):
    """Check review persistence and foreign keys."""
    model = 'Review'
    field = 'text'
