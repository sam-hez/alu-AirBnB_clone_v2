#!/usr/bin/python3
"""Verify every mapped model with independent SQL queries."""
import unittest
from datetime import datetime
from models import storage, storage_t
from tests.test_db_support import DatabaseFixture
from models.state import State
from models.city import City


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

    def test_cities_relationship(self):
        """Cities point back to their state and exclude other states."""
        state = self.objects['State']
        city = self.objects['City']
        other = State(name='Nevada')
        other.save()
        self.assertEqual(state.cities, [city])
        self.assertIs(city.state, state)
        self.assertEqual(other.cities, [])

    def test_delete_cascades_to_cities(self):
        """Deleting a reloaded state removes all of its cities."""
        state = State(name='Nevada')
        state.save()
        for name in ('Reno', 'Las Vegas'):
            City(name=name, state_id=state.id).save()
        state_id = state.id
        storage.close()
        state = storage.all(State)['State.' + state_id]
        state.delete()
        storage.save()
        self.assertEqual(self.sql_value(
            'SELECT COUNT(*) FROM states WHERE id = %s', (state_id,)), 0)
        self.assertEqual(self.sql_value(
            'SELECT COUNT(*) FROM cities WHERE state_id = %s',
            (state_id,)), 0)
        self.assertEqual(self.sql_value('SELECT COUNT(*) FROM cities'), 1)


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


@unittest.skipIf(storage_t != 'db', 'Requires database storage.')
class TestDBUserPlaces(DatabaseFixture, unittest.TestCase):
    """Check required fields, optional values, and place relationships."""

    def test_user_required_fields(self):
        """Both email and password are required to save a user."""
        from models.user import User
        from sqlalchemy.exc import IntegrityError, OperationalError
        for values in ({'email': 'test@example.com'}, {'password': 'test'}):
            with self.assertRaises((IntegrityError, OperationalError)):
                User(**values).save()
        self.assertEqual(self.sql_value('SELECT COUNT(*) FROM users'), 1)

    def test_user_optional_names(self):
        """A user can be saved without first and last names."""
        user = self.objects['User']
        for field in ('first_name', 'last_name'):
            self.assertIsNone(self.sql_value(
                'SELECT ' + field + ' FROM users WHERE id = %s', (user.id,)))

    def test_place_required_fields(self):
        """Missing names or parent IDs and invalid IDs reject a place."""
        from models.place import Place
        from sqlalchemy.exc import IntegrityError, OperationalError
        values = {'name': 'Home', 'city_id': self.objects['City'].id,
                  'user_id': self.objects['User'].id}
        for field in values:
            incomplete = values.copy()
            del incomplete[field]
            with self.assertRaises((IntegrityError, OperationalError)):
                Place(**incomplete).save()
        for field in ('city_id', 'user_id'):
            invalid = values.copy()
            invalid[field] = 'missing'
            with self.assertRaises((IntegrityError, OperationalError)):
                Place(**invalid).save()
        self.assertEqual(self.sql_value('SELECT COUNT(*) FROM places'), 1)

    def test_place_defaults(self):
        """Counts default to zero and optional data is stored as NULL."""
        place = self.objects['Place']
        for field in ('number_rooms', 'number_bathrooms',
                      'max_guest', 'price_by_night'):
            self.assertEqual(self.sql_value(
                'SELECT ' + field + ' FROM places WHERE id = %s',
                (place.id,)), 0)
        for field in ('description', 'latitude', 'longitude'):
            self.assertIsNone(self.sql_value(
                'SELECT ' + field + ' FROM places WHERE id = %s',
                (place.id,)))

    def test_relationships(self):
        """Places link to their owners and cities in both directions."""
        place = self.objects['Place']
        user = self.objects['User']
        city = self.objects['City']
        self.assertEqual(user.places, [place])
        self.assertEqual(city.places, [place])
        self.assertIs(place.user, user)
        self.assertIs(place.cities, city)

    def check_cascade(self, parent_name):
        """Delete a separate parent and verify only its places disappear."""
        from models.user import User
        from models.place import Place
        user = User(email='other@example.com', password='test')
        user.save()
        city = City(name='Other city', state_id=self.objects['State'].id)
        city.save()
        for name in ('House', 'Apartment'):
            Place(name=name, user_id=user.id, city_id=city.id).save()
        parent = user if parent_name == 'User' else city
        parent_id = parent.id
        table = parent.__tablename__
        field = 'user_id' if parent_name == 'User' else 'city_id'
        storage.close()
        parent = storage.all(parent_name)[parent_name + '.' + parent_id]
        parent.delete()
        storage.save()
        self.assertEqual(self.sql_value(
            'SELECT COUNT(*) FROM ' + table + ' WHERE id = %s',
            (parent_id,)), 0)
        self.assertEqual(self.sql_value(
            'SELECT COUNT(*) FROM places WHERE ' + field + ' = %s',
            (parent_id,)), 0)
        self.assertEqual(self.sql_value('SELECT COUNT(*) FROM places'), 1)

    def test_delete_user_places(self):
        """Deleting an owner removes the owner's places."""
        self.check_cascade('User')

    def test_delete_city_places(self):
        """Deleting a city removes the city's places."""
        self.check_cascade('City')


@unittest.skipIf(storage_t != 'db', 'Requires database storage.')
class TestDBReviewsAmenities(DatabaseFixture, unittest.TestCase):
    """Verify review ownership and many-to-many amenity persistence."""

    def test_required_fields(self):
        """Incomplete reviews and unnamed amenities must not be saved."""
        from models.review import Review
        from models.amenity import Amenity
        from sqlalchemy.exc import IntegrityError, OperationalError
        values = {'text': 'Great', 'place_id': self.objects['Place'].id,
                  'user_id': self.objects['User'].id}
        for field in values:
            incomplete = values.copy()
            del incomplete[field]
            with self.assertRaises((IntegrityError, OperationalError)):
                Review(**incomplete).save()
        with self.assertRaises((IntegrityError, OperationalError)):
            Amenity().save()
        self.assertEqual(self.sql_value('SELECT COUNT(*) FROM reviews'), 1)
        self.assertEqual(self.sql_value('SELECT COUNT(*) FROM amenities'), 1)

    def test_review_relationships(self):
        """Reviews expose their author and place in both directions."""
        review = self.objects['Review']
        user = self.objects['User']
        place = self.objects['Place']
        self.assertEqual(user.reviews, [review])
        self.assertEqual(place.reviews, [review])
        self.assertIs(review.user, user)
        self.assertIs(review.place, place)

    def test_delete_place_reviews(self):
        """Removing a place also removes reviews but keeps the author."""
        self.objects['Place'].delete()
        storage.save()
        self.assertEqual(self.sql_value('SELECT COUNT(*) FROM reviews'), 0)
        self.assertEqual(self.sql_value('SELECT COUNT(*) FROM users'), 1)

    def test_delete_review_author(self):
        """Removing a reviewer preserves a place owned by another user."""
        from models.user import User
        from models.review import Review
        author = User(email='reviewer@example.com', password='test')
        author.save()
        Review(user_id=author.id, place_id=self.objects['Place'].id,
               text='Nice').save()
        author.delete()
        storage.save()
        self.assertEqual(self.sql_value('SELECT COUNT(*) FROM reviews'), 1)
        self.assertEqual(self.sql_value('SELECT COUNT(*) FROM places'), 1)

    def test_delete_owner_with_reviews(self):
        """Deleting an owner removes owned places and all their reviews."""
        self.objects['User'].delete()
        storage.save()
        self.assertEqual(self.sql_value('SELECT COUNT(*) FROM reviews'), 0)
        self.assertEqual(self.sql_value('SELECT COUNT(*) FROM places'), 0)

    def test_shared_amenities(self):
        """Two places share amenities through five distinct join rows."""
        from models.place import Place
        from models.amenity import Amenity
        first = self.objects['Place']
        second = Place(name='Second', city_id=first.city_id,
                       user_id=first.user_id)
        second.save()
        wifi = self.objects['Amenity']
        cable = Amenity(name='Cable')
        cable.save()
        oven = Amenity(name='Oven')
        oven.save()
        first.amenities.extend([wifi, cable])
        second.amenities.extend([wifi, cable, oven])
        storage.save()
        first_id, second_id, wifi_id = first.id, second.id, wifi.id
        self.assertEqual(self.sql_value(
            'SELECT COUNT(*) FROM place_amenity'), 5)
        storage.close()
        first = storage.all(Place)['Place.' + first_id]
        second = storage.all(Place)['Place.' + second_id]
        wifi = storage.all(Amenity)['Amenity.' + wifi_id]
        self.assertEqual(len(first.amenities), 2)
        self.assertEqual(len(second.amenities), 3)
        self.assertCountEqual(wifi.place_amenities, [first, second])
        first.amenities.remove(wifi)
        storage.save()
        self.assertEqual(self.sql_value(
            'SELECT COUNT(*) FROM place_amenity'), 4)
        first.delete()
        storage.save()
        self.assertEqual(self.sql_value(
            'SELECT COUNT(*) FROM place_amenity'), 3)
        self.assertEqual(self.sql_value('SELECT COUNT(*) FROM amenities'), 3)
        wifi.delete()
        storage.save()
        self.assertEqual(self.sql_value(
            'SELECT COUNT(*) FROM place_amenity'), 2)
        self.assertEqual(self.sql_value('SELECT COUNT(*) FROM places'), 1)
