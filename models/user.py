#!/usr/bin/python3
"""Define the User model for file and database storage."""
import os
from models.base_model import BaseModel, Base

if os.getenv('HBNB_TYPE_STORAGE') == 'db':
    from sqlalchemy import Column, String
    from sqlalchemy.orm import relationship


class User(BaseModel, Base):
    """Represent a user using the selected storage engine."""

    if os.getenv('HBNB_TYPE_STORAGE') == 'db':
        __tablename__ = 'users'
        email = Column(String(128), nullable=False)
        password = Column(String(128), nullable=False)
        first_name = Column(String(128))
        last_name = Column(String(128))
        places = relationship('Place', backref='user',
                              cascade='all, delete-orphan')
        reviews = relationship('Review', backref='user',
                               cascade='all, delete-orphan')
    else:
        email = ''
        password = ''
        first_name = ''
        last_name = ''
