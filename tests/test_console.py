#!/usr/bin/python3
"""Regression tests for the inherited console and shared file storage."""
import io
import json
import os
import tempfile
import unittest
from models import storage_t
from unittest.mock import patch

import models
from console import HBNBCommand, storage
from models.engine.file_storage import FileStorage
from models.place import Place
from models.user import User


@unittest.skipIf(storage_t == 'db', 'Tests JSON file storage only.')
class TestConsole(unittest.TestCase):
    """Check console operations using temporary storage files."""

    def setUp(self):
        """Isolate stored objects and capture command output."""
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.path = os.path.join(directory.name, 'file.json')
        for name, value in (('_FileStorage__file_path', self.path),
                            ('_FileStorage__objects', {})):
            patcher = patch.object(FileStorage, name, value)
            patcher.start()
            self.addCleanup(patcher.stop)
        self.console = HBNBCommand()

    def run_command(self, command):
        """Execute normal or dotted syntax and return the printed output."""
        with patch('sys.stdout', new_callable=io.StringIO) as output:
            self.console.onecmd(self.console.precmd(command))
        return output.getvalue()

    def test_shared_storage(self):
        """Console and models must use the same storage instance."""
        self.assertIs(storage, models.storage)

    def test_create_saves_once(self):
        """Creating an object prints its ID and saves exactly once."""
        with patch.object(storage, 'save', wraps=storage.save) as save:
            obj_id = self.run_command('create User').strip()
        save.assert_called_once_with()
        with open(self.path) as file:
            data = json.load(file)
        self.assertIn('User.' + obj_id, data)

    def test_update_zero_in_dictionary(self):
        """A dictionary update accepts zero as a numeric value."""
        obj = Place()
        obj.number_rooms = 3
        result = self.run_command(
            'Place.update("{}", {{"number_rooms": 0}})'.format(obj.id))
        self.assertEqual(result, '')
        self.assertEqual(obj.number_rooms, 0)
        with open(self.path) as file:
            data = json.load(file)
        self.assertEqual(data['Place.' + obj.id]['number_rooms'], 0)

    def test_update_quoted_value(self):
        """Names containing spaces retain the complete value."""
        obj = User()
        self.run_command('update User {} first_name "Betty Smith"'.format(
            obj.id))
        self.assertEqual(obj.first_name, 'Betty Smith')

    def test_show_and_destroy(self):
        """Dotted commands show and delete the requested instance."""
        obj = User()
        self.assertEqual(self.run_command('User.show("{}")'.format(obj.id)),
                         str(obj) + '\n')
        self.run_command('User.destroy("{}")'.format(obj.id))
        self.assertNotIn('User.' + obj.id, storage.all())
        with open(self.path) as file:
            self.assertEqual(json.load(file), {})
