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
from models.state import State
from models.city import City


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
        obj.save()
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
        obj.save()
        self.run_command('update User {} first_name "Betty Smith"'.format(
            obj.id))
        self.assertEqual(obj.first_name, 'Betty Smith')

    def test_show_and_destroy(self):
        """Dotted commands show and delete the requested instance."""
        obj = User()
        obj.save()
        self.assertEqual(self.run_command('User.show("{}")'.format(obj.id)),
                         str(obj) + '\n')
        self.run_command('User.destroy("{}")'.format(obj.id))
        self.assertNotIn('User.' + obj.id, storage.all())
        with open(self.path) as file:
            self.assertEqual(json.load(file), {})

    def test_create_place_parameters(self):
        """The assignment's Place example preserves values and types."""
        obj_id = self.run_command(
            'create Place city_id="0001" user_id="0001" '
            'name="My_little_house" number_rooms=4 number_bathrooms=2 '
            'max_guest=10 price_by_night=300 latitude=37.773972 '
            'longitude=-122.431297').strip()
        expected = {
            'city_id': '0001', 'user_id': '0001', 'name': 'My little house',
            'number_rooms': 4, 'number_bathrooms': 2, 'max_guest': 10,
            'price_by_night': 300, 'latitude': 37.773972,
            'longitude': -122.431297,
        }
        obj = storage.all()['Place.' + obj_id]
        with open(self.path) as file:
            saved = json.load(file)['Place.' + obj_id]
        for key, value in expected.items():
            with self.subTest(attribute=key):
                self.assertEqual(getattr(obj, key), value)
                self.assertIs(type(getattr(obj, key)), type(value))
                self.assertEqual(saved[key], value)

    def test_create_types_follow_values(self):
        """Custom attributes and quoted numbers use value-based types."""
        obj_id = self.run_command(
            'create BaseModel count=7 rating=4.5 code="007" '
            'number_rooms="4" zero=0 negative=-3 fraction=-0.25').strip()
        obj = storage.all()['BaseModel.' + obj_id]
        expected = {'count': 7, 'rating': 4.5, 'code': '007',
                    'number_rooms': '4', 'zero': 0, 'negative': -3,
                    'fraction': -0.25}
        for key, value in expected.items():
            with self.subTest(attribute=key):
                self.assertEqual(getattr(obj, key), value)
                self.assertIs(type(getattr(obj, key)), type(value))

    def test_create_escaped_quotes(self):
        """Escaped double quotes remain within the stored string."""
        obj_id = self.run_command(
            r'create State name="The_\"Golden\"_State"').strip()
        self.assertEqual(storage.all()['State.' + obj_id].name,
                         'The "Golden" State')

    def test_create_empty_string(self):
        """Empty quoted strings are valid parameter values."""
        obj_id = self.run_command('create State name=""').strip()
        self.assertEqual(storage.all()['State.' + obj_id].name, '')

    def test_create_skips_invalid_parameters(self):
        """Malformed parameters do not prevent valid ones being saved."""
        obj_id = self.run_command(
            'create State bad=word missing empty= decimal=1.2.3 '
            'single=\'quoted\' =5 9key=2 numeric=1_000 '
            'name="New_York" population=10').strip()
        obj = storage.all()['State.' + obj_id]
        self.assertEqual(obj.name, 'New York')
        self.assertEqual(obj.population, 10)
        for key in ('bad', 'missing', 'empty', 'decimal', 'single',
                    '9key', 'numeric'):
            self.assertNotIn(key, obj.__dict__)

    def test_create_skips_broken_quotes(self):
        """Broken strings are skipped while later numeric values survive."""
        obj_id = self.run_command(
            'create State bad="unfinished population=10').strip()
        obj = storage.all()['State.' + obj_id]
        self.assertNotIn('bad', obj.__dict__)
        self.assertEqual(obj.population, 10)

    def test_create_skips_trailing_string_text(self):
        """Characters after a closing quote make that parameter invalid."""
        obj_id = self.run_command(
            'create State bad="value"extra name="Arizona"').strip()
        obj = storage.all()['State.' + obj_id]
        self.assertNotIn('bad', obj.__dict__)
        self.assertEqual(obj.name, 'Arizona')

    def test_create_class_errors(self):
        """Missing or unknown classes report errors without saving."""
        self.assertEqual(self.run_command('create'),
                         '** class name missing **\n')
        self.assertEqual(self.run_command('create Unknown name="Test"'),
                         "** class doesn't exist **\n")
        self.assertEqual(storage.all(), {})
        self.assertFalse(os.path.exists(self.path))


class TestCreateParameters(unittest.TestCase):
    """Check parameter parsing with either storage engine."""

    def create(self, command, model):
        """Capture the constructed object without writing to storage."""
        with patch.object(model, 'save', autospec=True) as save:
            with patch('sys.stdout', new_callable=io.StringIO) as output:
                HBNBCommand().onecmd(command)
        save.assert_called_once()
        obj = save.call_args[0][0]
        self.assertEqual(output.getvalue().strip(), obj.id)
        return obj

    def test_create_state_name(self):
        """A quoted state name must reach the saved object."""
        state = self.create('create State name="California"', State)
        self.assertEqual(state.name, 'California')

    def test_create_city_parameters(self):
        """Creation must process both state_id and name."""
        city = self.create(
            'create City state_id="existing-state" name="Fremont"', City)
        self.assertEqual(city.state_id, 'existing-state')
        self.assertEqual(city.name, 'Fremont')

    def test_create_city_spaces(self):
        """Underscores in quoted names become spaces."""
        city = self.create(
            'create City state_id="existing-state" name="San_Francisco"',
            City)
        self.assertEqual(city.state_id, 'existing-state')
        self.assertEqual(city.name, 'San Francisco')

    def test_create_place_numbers(self):
        """Creation preserves integer and float values before persistence."""
        place = self.create(
            'create Place city_id="city" user_id="user" name="My_house" '
            'description="no_description_yet" number_rooms=4 '
            'number_bathrooms=1 max_guest=3 price_by_night=100 '
            'latitude=120.12 longitude=101.4', Place)
        for field, value in (('number_rooms', 4), ('number_bathrooms', 1),
                             ('max_guest', 3), ('price_by_night', 100),
                             ('latitude', 120.12), ('longitude', 101.4)):
            self.assertEqual(getattr(place, field), value)
            self.assertIs(type(getattr(place, field)), type(value))
