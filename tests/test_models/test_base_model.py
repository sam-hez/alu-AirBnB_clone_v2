#!/usr/bin/python3
"""Test the base model model behavior."""
from models.base_model import BaseModel
import unittest
import datetime
from uuid import UUID
import json
import os
import tempfile
from unittest.mock import patch
from models.engine.file_storage import FileStorage


class test_basemodel(unittest.TestCase):
    """Check model defaults and inherited behavior."""

    def __init__(self, *args, **kwargs):
        """Select the model class used by these tests."""
        super().__init__(*args, **kwargs)
        self.name = 'BaseModel'
        self.value = BaseModel

    def setUp(self):
        """Use temporary storage without changing application data."""
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.path = os.path.join(directory.name, 'file.json')
        for name, value in (('_FileStorage__file_path', self.path),
                            ('_FileStorage__objects', {})):
            patcher = patch.object(FileStorage, name, value)
            patcher.start()
            self.addCleanup(patcher.stop)

    def test_default(self):
        """Check default behavior."""
        i = self.value()
        self.assertEqual(type(i), self.value)

    def test_kwargs(self):
        """Check kwargs behavior."""
        i = self.value()
        copy = i.to_dict()
        new = BaseModel(**copy)
        self.assertFalse(new is i)

    def test_kwargs_int(self):
        """Check kwargs int behavior."""
        i = self.value()
        copy = i.to_dict()
        copy.update({1: 2})
        with self.assertRaises(TypeError):
            new = BaseModel(**copy)

    def test_save(self):
        """ Testing save """
        i = self.value()
        i.save()
        key = self.name + "." + i.id
        with open(self.path, 'r') as f:
            j = json.load(f)
            self.assertEqual(j[key], i.to_dict())

    def test_str(self):
        """Check str behavior."""
        i = self.value()
        self.assertEqual(str(i), '[{}] ({}) {}'.format(self.name, i.id,
                         i.__dict__))

    def test_todict(self):
        """Check todict behavior."""
        i = self.value()
        n = i.to_dict()
        self.assertEqual(i.to_dict(), n)

    def test_kwargs_none(self):
        """Check kwargs none behavior."""
        n = {None: None}
        with self.assertRaises(TypeError):
            new = self.value(**n)

    def test_kwargs_one(self):
        """Check kwargs one behavior."""
        n = {'Name': 'test'}
        with self.assertRaises(KeyError):
            new = self.value(**n)

    def test_id(self):
        """Check id behavior."""
        new = self.value()
        self.assertEqual(type(new.id), str)

    def test_created_at(self):
        """Check created at behavior."""
        new = self.value()
        self.assertEqual(type(new.created_at), datetime.datetime)

    def test_updated_at(self):
        """Check updated at behavior."""
        new = self.value()
        self.assertEqual(type(new.updated_at), datetime.datetime)
        n = new.to_dict()
        new = BaseModel(**n)
        self.assertEqual(new.created_at.isoformat(), n['created_at'])
        self.assertEqual(new.updated_at.isoformat(), n['updated_at'])

    def test_round_trip_without_microseconds(self):
        """Restore ISO timestamps even when microseconds are zero."""
        obj = self.value()
        obj.created_at = datetime.datetime(2026, 1, 1)
        obj.updated_at = datetime.datetime(2026, 1, 2)
        restored = self.value(**obj.to_dict())
        self.assertEqual(restored.to_dict(), obj.to_dict())

    def test_unique_ids(self):
        """New instances have different valid UUIDs."""
        first = self.value()
        second = self.value()
        self.assertNotEqual(first.id, second.id)
        self.assertEqual(UUID(first.id).version, 4)

    def test_to_dict_does_not_change_object(self):
        """Converting attributes leaves datetime values on the object."""
        obj = self.value()
        data = obj.to_dict()
        data['id'] = 'changed'
        self.assertNotEqual(obj.id, 'changed')
        self.assertIsInstance(obj.created_at, datetime.datetime)
        self.assertNotIn('__class__', obj.__dict__)
