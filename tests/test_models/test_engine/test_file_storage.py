#!/usr/bin/python3
""" Module for testing file storage"""
import unittest
from models import storage_t
from models.base_model import BaseModel
from models import storage
import os
import tempfile
from unittest.mock import patch
from models.engine.file_storage import FileStorage


@unittest.skipIf(storage_t == 'db', 'Tests JSON file storage only.')
class test_fileStorage(unittest.TestCase):
    """ Class to test the file storage method """

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

    def test_obj_list_empty(self):
        """ __objects is initially empty """
        self.assertEqual(len(storage.all()), 0)

    def test_new(self):
        """ New object is correctly added to __objects """
        new = BaseModel()
        self.assertIs(storage.all()["BaseModel." + new.id], new)

    def test_all(self):
        """ __objects is properly returned """
        new = BaseModel()
        temp = storage.all()
        self.assertIsInstance(temp, dict)

    def test_base_model_instantiation(self):
        """ File is not created on BaseModel save """
        new = BaseModel()
        self.assertFalse(os.path.exists(self.path))

    def test_empty(self):
        """ Data is saved to file """
        new = BaseModel()
        thing = new.to_dict()
        new.save()
        new2 = BaseModel(**thing)
        self.assertNotEqual(os.path.getsize(self.path), 0)

    def test_save(self):
        """ FileStorage save method """
        new = BaseModel()
        storage.save()
        self.assertTrue(os.path.exists(self.path))

    def test_reload(self):
        """ Storage file is successfully loaded to __objects """
        new = BaseModel()
        storage.save()
        storage.all().clear()
        storage.reload()
        for obj in storage.all().values():
            loaded = obj
        self.assertEqual(new.to_dict()['id'], loaded.to_dict()['id'])

    def test_reload_empty(self):
        """ Load from an empty file """
        with open(self.path, 'w') as f:
            pass
        with self.assertRaises(ValueError):
            storage.reload()

    def test_reload_from_nonexistent(self):
        """ Nothing happens if file does not exist """
        self.assertEqual(storage.reload(), None)

    def test_base_model_save(self):
        """ BaseModel save method calls storage save """
        new = BaseModel()
        new.save()
        self.assertTrue(os.path.exists(self.path))

    def test_type_path(self):
        """ Confirm __file_path is string """
        self.assertEqual(type(storage._FileStorage__file_path), str)

    def test_type_objects(self):
        """ Confirm __objects is a dict """
        self.assertEqual(type(storage.all()), dict)

    def test_key_format(self):
        """ Key is properly formatted """
        new = BaseModel()
        _id = new.to_dict()['id']
        for key in storage.all().keys():
            temp = key
        self.assertEqual(temp, 'BaseModel' + '.' + _id)

    def test_storage_var_created(self):
        """ FileStorage object storage created """
        from models.engine.file_storage import FileStorage
        self.assertEqual(type(storage), FileStorage)

    def test_filter_class(self):
        """File storage filters by either class object or class name."""
        from models.user import User
        base = BaseModel()
        user = User()
        expected = {'User.' + user.id: user}
        self.assertEqual(storage.all(User), expected)
        self.assertEqual(storage.all('User'), expected)
        self.assertIn('BaseModel.' + base.id, storage.all())

    def test_delete(self):
        """Deleting an object removes it without changing other objects."""
        first = BaseModel()
        second = BaseModel()
        first.delete()
        storage.save()
        storage.all().clear()
        storage.reload()
        self.assertNotIn('BaseModel.' + first.id, storage.all())
        self.assertIn('BaseModel.' + second.id, storage.all())

    def test_close(self):
        """Closing file storage reloads the saved object data."""
        obj = BaseModel()
        obj.save()
        storage.all().clear()
        storage.close()
        self.assertIn('BaseModel.' + obj.id, storage.all())
