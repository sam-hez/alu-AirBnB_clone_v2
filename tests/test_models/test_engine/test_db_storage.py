#!/usr/bin/python3
"""Check the database storage engine against real MySQL rows."""
import unittest
from models import storage, storage_t
from models.state import State
from tests.test_db_support import DatabaseFixture


@unittest.skipIf(storage_t != 'db', 'Requires database storage.')
class TestDBStorage(DatabaseFixture, unittest.TestCase):
    """Exercise session operations and persistence through MySQL."""

    def test_engine_selected(self):
        """The environment selects the real database engine."""
        from models.engine.db_storage import DBStorage
        self.assertIsInstance(storage, DBStorage)

    def test_all_models(self):
        """All includes instances from each mapped table."""
        self.assertEqual(len(storage.all()), 6)

    def test_new_and_save(self):
        """A commit inserts a row visible through an independent driver."""
        obj = State(name='Arizona')
        storage.new(obj)
        self.assertEqual(self.sql_value('SELECT COUNT(*) FROM states'), 1)
        storage.save()
        self.assertEqual(self.sql_value('SELECT COUNT(*) FROM states'), 2)

    def test_delete_none(self):
        """Deleting no object leaves persisted rows unchanged."""
        storage.delete()
        storage.save()
        self.assertEqual(len(storage.all()), 6)

    def test_close_and_reload(self):
        """A fresh session retrieves already committed rows."""
        state = self.objects['State']
        storage.close()
        storage.reload()
        restored = storage.all(State)['State.' + state.id]
        self.assertEqual(restored.name, state.name)
        self.assertIsNot(restored, state)

    def test_failed_commit_recovers(self):
        """A failed insert rolls back so later valid inserts can succeed."""
        from sqlalchemy.exc import IntegrityError
        from models.city import City
        invalid = City(name='Invalid', state_id='missing-state')
        storage.new(invalid)
        with self.assertRaises(IntegrityError):
            storage.save()
        State(name='Nevada').save()
        self.assertEqual(self.sql_value('SELECT COUNT(*) FROM states'), 2)

    def test_close_refreshes_external_inserts(self):
        """Closing exposes rows committed by an independent connection."""
        self.assertEqual(len(storage.all(State)), 1)
        for index in (1, 2):
            with self.connection.cursor() as cursor:
                cursor.execute(
                    'INSERT INTO states (id, name, created_at, updated_at) '
                    'VALUES (%s, %s, NOW(), NOW())',
                    ('external-state-' + str(index), 'External'))
            storage.close()
            self.assertEqual(len(storage.all(State)), 1 + index)
