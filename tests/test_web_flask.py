#!/usr/bin/python3
"""Verify the Flask states list with database-backed requests."""
import importlib
import importlib.util
import re
import unittest
from unittest.mock import patch
from models import storage, storage_t
from tests.test_db_support import DatabaseFixture


@unittest.skipIf(storage_t != 'db', 'Requires database storage.')
@unittest.skipIf(importlib.util.find_spec('flask') is None,
                 'Requires Flask to test web responses.')
class TestStatesList(DatabaseFixture, unittest.TestCase):
    """Check state counts, sorting, and fresh data between requests."""

    def setUp(self):
        """Prepare the dedicated test database and import the Flask app."""
        super().setUp()
        self.clear_database()
        module = importlib.import_module('web_flask.7-states_list')
        self.client = module.app.test_client()

    def insert_states(self, number, start=0):
        """Insert states using an independent database connection."""
        rows = [('web-state-{}'.format(index),
                 'State {:03d}'.format(index))
                for index in reversed(range(start, start + number))]
        with self.connection.cursor() as cursor:
            cursor.executemany(
                'INSERT INTO states (id, name, created_at, updated_at) '
                'VALUES (%s, %s, NOW(), NOW())', rows)
        return sorted(rows, key=lambda row: row[1])

    def request_states(self, path='/states_list'):
        """Fetch the page and confirm its storage session is released."""
        with patch.object(storage, 'close', wraps=storage.close) as close:
            response = self.client.get(path)
            close.assert_called_once_with()
        self.assertEqual(response.status_code, 200)
        html = response.data.decode()
        self.assertIn('<H1>States</H1>', html)
        return re.findall(r'<LI>([^:]+): <B>(.*?)</B></LI>', html)

    def test_state_counts_and_sorting(self):
        """Zero, five, and one hundred states render in alphabetical order."""
        for count in (0, 5, 100):
            self.clear_database()
            expected = self.insert_states(count) if count else []
            self.assertEqual(self.request_states(), expected)

    def test_external_insert_between_requests(self):
        """Show a new state on the next request without restarting."""
        expected = self.insert_states(5)
        self.assertEqual(self.request_states(), expected)
        expected += self.insert_states(1, start=5)
        self.assertEqual(self.request_states(), expected)

    def test_trailing_slash(self):
        """The route accepts a trailing slash without a redirect."""
        expected = self.insert_states(5)
        self.assertEqual(self.request_states('/states_list/'), expected)
