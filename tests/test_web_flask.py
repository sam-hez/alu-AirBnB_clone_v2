#!/usr/bin/python3
"""Verify the Flask states list with database-backed requests."""
import importlib
import importlib.util
import re
import unittest
from unittest.mock import patch
from xml.etree import ElementTree
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


@unittest.skipIf(storage_t != 'db', 'Requires database storage.')
@unittest.skipIf(importlib.util.find_spec('flask') is None,
                 'Requires Flask to test web responses.')
class TestCitiesByStates(DatabaseFixture, unittest.TestCase):
    """Check sorted states and cities with fresh database requests."""

    def setUp(self):
        """Prepare the test database and cities application."""
        super().setUp()
        self.clear_database()
        module = importlib.import_module('web_flask.8-cities_by_states')
        self.client = module.app.test_client()

    def insert_states_and_cities(self, city_counts, start=0):
        """Insert unsorted data through an independent SQL connection."""
        states = []
        with self.connection.cursor() as cursor:
            for index in reversed(range(len(city_counts))):
                number = start + index
                state_id = 'state-{}'.format(number)
                name = 'State {:03d}'.format(number)
                cursor.execute(
                    'INSERT INTO states (id, name, created_at, updated_at) '
                    'VALUES (%s, %s, NOW(), NOW())', (state_id, name))
                cities = []
                for city_index in reversed(range(city_counts[index])):
                    city_id = 'city-{}-{}'.format(number, city_index)
                    city_name = 'City {:03d}'.format(city_index)
                    cursor.execute(
                        'INSERT INTO cities '
                        '(id, name, state_id, created_at, updated_at) '
                        'VALUES (%s, %s, %s, NOW(), NOW())',
                        (city_id, city_name, state_id))
                    cities.append((city_id, city_name))
                cities.sort(key=lambda city: city[1])
                states.append((state_id, name, cities))
        return sorted(states, key=lambda state: state[1])

    def request_cities(self, path='/cities_by_states'):
        """Read nested state and city lists and confirm session cleanup."""
        with patch.object(storage, 'close', wraps=storage.close) as close:
            response = self.client.get(path)
            close.assert_called_once_with()
        self.assertEqual(response.status_code, 200)
        page = ElementTree.fromstring(response.data.decode())
        self.assertEqual(page.find('BODY/H1').text, 'States')
        states = []
        for state in page.findall('BODY/UL/LI'):
            cities = [(city.text.strip().rstrip(':'), city.find('B').text)
                      for city in state.findall('UL/LI')]
            states.append((state.text.strip().rstrip(':'),
                           state.find('B').text, cities))
        return states

    def test_city_counts_and_sorting(self):
        """Render empty, small, and large datasets in alphabetical order."""
        for counts in ([2] * 5, [2, 2, 0, 2, 2], [0] * 5, [],
                       [index % 11 for index in range(100)]):
            with self.subTest(city_counts=counts):
                self.clear_database()
                expected = self.insert_states_and_cities(counts)
                self.assertEqual(self.request_cities(), expected)

    def test_external_insert_between_requests(self):
        """Show a newly inserted state and its cities without restarting."""
        expected = self.insert_states_and_cities([2] * 3)
        self.assertEqual(self.request_cities(), expected)
        expected += self.insert_states_and_cities([4], start=3)
        self.assertEqual(self.request_cities(), expected)

    def test_trailing_slash(self):
        """Accept a trailing slash without redirecting the request."""
        expected = self.insert_states_and_cities([2])
        self.assertEqual(self.request_cities('/cities_by_states/'), expected)
