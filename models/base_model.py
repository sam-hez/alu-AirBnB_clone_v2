#!/usr/bin/python3
"""Define shared identifiers, timestamps, and persistence methods."""
import os
import uuid
from datetime import datetime

if os.getenv('HBNB_TYPE_STORAGE') == 'db':
    from sqlalchemy import Column, DateTime, String
    from sqlalchemy.orm import declarative_base
    Base = declarative_base()
else:
    Base = object


class BaseModel:
    """Provide attributes shared by file and database models."""

    if os.getenv('HBNB_TYPE_STORAGE') == 'db':
        id = Column(String(60), primary_key=True, nullable=False)
        created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
        updated_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    def __init__(self, *args, **kwargs):
        """Create an instance or restore its serialized attributes."""
        self.id = str(uuid.uuid4())
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        if hasattr(self, '__table__'):
            for column in self.__table__.columns:
                if column.default is not None and column.default.is_scalar:
                    setattr(self, column.name, column.default.arg)
        for key, value in kwargs.items():
            if key in ('__class__', '_sa_instance_state'):
                continue
            if key in ('created_at', 'updated_at') and isinstance(value, str):
                value = datetime.fromisoformat(value)
            setattr(self, key, value)

    def __str__(self):
        """Return the class name, ID, and instance attributes."""
        return '[{}] ({}) {}'.format(
            type(self).__name__, self.id, self.__dict__)

    def save(self):
        """Register this instance and persist its updated timestamp."""
        from models import storage
        self.updated_at = datetime.now()
        storage.new(self)
        storage.save()

    def delete(self):
        """Mark this instance for removal from storage."""
        from models import storage
        storage.delete(self)

    def to_dict(self):
        """Return serializable attributes without SQLAlchemy internals."""
        data = self.__dict__.copy()
        data.pop('_sa_instance_state', None)
        data['__class__'] = type(self).__name__
        data['created_at'] = self.created_at.isoformat()
        data['updated_at'] = self.updated_at.isoformat()
        return data
