#!/usr/bin/python3
"""Persist model instances in MySQL using SQLAlchemy."""
import os
from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from sqlalchemy.orm import scoped_session, sessionmaker
from models.base_model import Base
from models.user import User
from models.state import State
from models.city import City
from models.place import Place
from models.amenity import Amenity
from models.review import Review


class DBStorage:
    """Provide the same storage operations as the JSON engine."""

    __engine = None
    __session = None
    classes = (User, State, City, Place, Amenity, Review)

    def __init__(self):
        """Connect using environment variables and reset only in test mode."""
        url = URL.create(
            'mysql+mysqldb', username=os.getenv('HBNB_MYSQL_USER'),
            password=os.getenv('HBNB_MYSQL_PWD'),
            host=os.getenv('HBNB_MYSQL_HOST', 'localhost'),
            port=int(os.getenv('HBNB_MYSQL_PORT', '3306')),
            database=os.getenv('HBNB_MYSQL_DB'))
        self.__engine = create_engine(url, pool_pre_ping=True)
        if os.getenv('HBNB_ENV') == 'test':
            Base.metadata.drop_all(self.__engine)

    def all(self, cls=None):
        """Return stored objects, optionally filtered by class or name."""
        objects = {}
        for model in self.classes:
            if cls is None or cls == model or cls == model.__name__:
                for obj in self.__session.query(model).all():
                    objects['{}.{}'.format(type(obj).__name__, obj.id)] = obj
        return objects

    def new(self, obj):
        """Add an instance to the current session."""
        self.__session.add(obj)

    def save(self):
        """Commit pending changes and recover the session after errors."""
        try:
            self.__session.commit()
        except Exception:
            self.__session.rollback()
            raise

    def delete(self, obj=None):
        """Mark an instance for deletion if one was provided."""
        if obj is not None:
            self.__session.delete(obj)

    def reload(self):
        """Create missing tables and start a scoped session."""
        Base.metadata.create_all(self.__engine)
        if self.__session is not None:
            self.__session.remove()
        factory = sessionmaker(bind=self.__engine, expire_on_commit=False)
        self.__session = scoped_session(factory)

    def close(self):
        """Release the session and its pending transaction."""
        self.__session.remove()
