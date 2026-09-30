#!/usr/bin/python3
"""Test console commands against real MySQL records."""
import io
import unittest
from unittest.mock import patch
from console import HBNBCommand
from models import storage, storage_t
from tests.test_db_support import DatabaseFixture


@unittest.skipIf(storage_t != 'db', 'Requires database storage.')
class TestDBConsole(DatabaseFixture, unittest.TestCase):
    """Confirm console actions insert, query, update, and delete rows."""

    def run_command(self, command):
        """Capture the output of a standard or dotted command."""
        console = HBNBCommand()
        with patch('sys.stdout', new_callable=io.StringIO) as output:
            console.onecmd(console.precmd(command))
        return output.getvalue()

    def test_create(self):
        """Creating a state adds exactly one row with the given name."""
        before = self.sql_value('SELECT COUNT(*) FROM states')
        obj_id = self.run_command('create State name="New_York"').strip()
        self.assertEqual(self.sql_value('SELECT COUNT(*) FROM states'),
                         before + 1)
        self.assertEqual(self.sql_value(
            'SELECT name FROM states WHERE id = %s', (obj_id,)), 'New York')

    def test_show(self):
        """Show finds a database instance by class and ID."""
        obj = self.objects['State']
        output = self.run_command('show State ' + obj.id)
        self.assertIn(obj.id, output)
        self.assertIn('California', output)

    def test_all(self):
        """All limits database results to the requested class."""
        output = self.run_command('all State')
        self.assertIn(self.objects['State'].id, output)
        self.assertNotIn(self.objects['User'].id, output)

    def test_update(self):
        """Update persists an attribute change rather than only memory."""
        obj = self.objects['State']
        self.run_command('update State {} name "Nevada"'.format(obj.id))
        self.assertEqual(self.sql_value(
            'SELECT name FROM states WHERE id = %s', (obj.id,)), 'Nevada')

    def test_destroy(self):
        """Destroy removes a row through the database storage API."""
        obj = self.objects['Review']
        self.run_command('destroy Review ' + obj.id)
        self.assertEqual(self.sql_value(
            'SELECT COUNT(*) FROM reviews WHERE id = %s', (obj.id,)), 0)

    def test_dictionary_update(self):
        """Dotted dictionary updates persist numeric zero values."""
        obj = self.objects['Place']
        obj.number_rooms = 3
        obj.save()
        self.run_command(
            'Place.update("{}", {{"number_rooms": 0}})'.format(obj.id))
        self.assertEqual(self.sql_value(
            'SELECT number_rooms FROM places WHERE id = %s', (obj.id,)), 0)

    def test_count(self):
        """Dotted count returns the number of rows for a model."""
        self.assertEqual(self.run_command('State.count()'), '1\n')

    def test_missing_object(self):
        """Unknown database IDs produce the expected console error."""
        self.assertEqual(self.run_command('show State missing'),
                         '** no instance found **\n')

    def test_create_state_without_name(self):
        """A missing state name must not insert a database row."""
        from sqlalchemy.exc import IntegrityError, OperationalError
        before = self.sql_value('SELECT COUNT(*) FROM states')
        with self.assertRaises((IntegrityError, OperationalError)) as error:
            self.run_command('create State')
        self.assertEqual(error.exception.orig.args[0], 1048)
        self.assertEqual(self.sql_value('SELECT COUNT(*) FROM states'),
                         before)

    def test_create_city_without_name(self):
        """An existing state_id cannot replace the required city name."""
        from sqlalchemy.exc import IntegrityError, OperationalError
        before = self.sql_value('SELECT COUNT(*) FROM cities')
        with self.assertRaises((IntegrityError, OperationalError)) as error:
            self.run_command('create City state_id="{}"'.format(
                self.objects['State'].id))
        self.assertEqual(error.exception.orig.args[0], 1048)
        self.assertEqual(self.sql_value('SELECT COUNT(*) FROM cities'),
                         before)

    def test_create_named_cities(self):
        """Both city parameters and converted spaces persist in MySQL."""
        state_id = self.run_command(
            'create State name="California"').strip()
        for name in ('Fremont', 'San_Francisco'):
            city_id = self.run_command(
                'create City state_id="{}" name="{}"'.format(
                    state_id, name)).strip()
            self.assertEqual(self.sql_value(
                'SELECT name FROM cities WHERE id = %s', (city_id,)),
                name.replace('_', ' '))
            self.assertEqual(self.sql_value(
                'SELECT state_id FROM cities WHERE id = %s', (city_id,)),
                state_id)
