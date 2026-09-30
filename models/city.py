#!/usr/bin/python3
"""Define the City model for file and database storage."""
import os
from models.base_model import BaseModel, Base

if os.getenv('HBNB_TYPE_STORAGE') == 'db':
    from sqlalchemy import Column, String, ForeignKey


class City(BaseModel, Base):
    """Represent a city using the selected storage engine."""

    if os.getenv('HBNB_TYPE_STORAGE') == 'db':
        __tablename__ = 'cities'
        state_id = Column(
            String(60), ForeignKey('states.id'), nullable=False, default='')
        name = Column(String(128), nullable=False, default='')
    else:
        state_id = ""
        name = ""
