#!/usr/bin/python3
"""Define the User model for file and database storage."""
import os
from models.base_model import BaseModel, Base

if os.getenv('HBNB_TYPE_STORAGE') == 'db':
    from sqlalchemy import Column, String, Integer, Float, ForeignKey


class User(BaseModel, Base):
    """Represent a user using the selected storage engine."""

    if os.getenv('HBNB_TYPE_STORAGE') == 'db':
        __tablename__ = 'users'
        email = Column(String(128), nullable=False, default='')
        password = Column(String(128), nullable=False, default='')
        first_name = Column(String(128), default='')
        last_name = Column(String(128), default='')
    else:
        email = ''
        password = ''
        first_name = ''
        last_name = ''
