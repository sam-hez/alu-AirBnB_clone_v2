#!/usr/bin/python3
"""Provide isolated fixtures and direct SQL checks for MySQL tests."""
import os
from models import storage
from models.state import State
from models.city import City
from models.user import User
from models.place import Place
from models.amenity import Amenity
from models.review import Review


class DatabaseFixture:
    """Build a small related dataset in the dedicated test database."""

    def setUp(self):
        """Prepare independent SQL access and valid related objects."""
        if (os.getenv('HBNB_ENV') != 'test'
                or os.getenv('HBNB_MYSQL_DB') != 'hbnb_test_db'):
            self.skipTest('Database integration requires hbnb_test_db.')
        import MySQLdb
        self.connection = MySQLdb.connect(
            host=os.getenv('HBNB_MYSQL_HOST', 'localhost'),
            port=int(os.getenv('HBNB_MYSQL_PORT', '3306')),
            user=os.getenv('HBNB_MYSQL_USER'),
            passwd=os.getenv('HBNB_MYSQL_PWD'),
            db=os.getenv('HBNB_MYSQL_DB'))
        self.connection.autocommit(True)
        self.addCleanup(self.connection.close)
        self.addCleanup(self.clear_database)
        self.clear_database()
        state = State(name='California')
        state.save()
        user = User(email='student@example.com', password='test-password')
        user.save()
        city = City(name='San Francisco', state_id=state.id)
        city.save()
        place = Place(name='Test house', city_id=city.id, user_id=user.id)
        place.save()
        amenity = Amenity(name='Wi-Fi')
        amenity.save()
        review = Review(text='Comfortable', place_id=place.id, user_id=user.id)
        review.save()
        self.objects = {type(obj).__name__: obj for obj in
                        (state, user, city, place, amenity, review)}

    def clear_database(self):
        """Clear only the dedicated test schema in dependency order."""
        storage.close()
        with self.connection.cursor() as cursor:
            for table in ('reviews', 'places', 'cities', 'amenities',
                          'states', 'users'):
                cursor.execute('DELETE FROM ' + table)

    def sql_value(self, query, values=()):
        """Read one scalar using the driver rather than the ORM."""
        with self.connection.cursor() as cursor:
            cursor.execute(query, values)
            return cursor.fetchone()[0]
