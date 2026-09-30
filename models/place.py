#!/usr/bin/python3
"""Define the Place model for file and database storage."""
import os
from models.base_model import BaseModel, Base

if os.getenv('HBNB_TYPE_STORAGE') == 'db':
    from sqlalchemy import Column, String, Integer, Float, ForeignKey


class Place(BaseModel, Base):
    """Represent a place using the selected storage engine."""

    if os.getenv('HBNB_TYPE_STORAGE') == 'db':
        __tablename__ = 'places'
        city_id = Column(
            String(60), ForeignKey('cities.id'), nullable=False, default='')
        user_id = Column(
            String(60), ForeignKey('users.id'), nullable=False, default='')
        name = Column(String(128), nullable=False, default='')
        description = Column(String(1024), default='')
        number_rooms = Column(Integer, nullable=False, default=0)
        number_bathrooms = Column(Integer, nullable=False, default=0)
        max_guest = Column(Integer, nullable=False, default=0)
        price_by_night = Column(Integer, nullable=False, default=0)
        latitude = Column(Float, nullable=False, default=0.0)
        longitude = Column(Float, nullable=False, default=0.0)
    else:
        city_id = ""
        user_id = ""
        name = ""
        description = ""
        number_rooms = 0
        number_bathrooms = 0
        max_guest = 0
        price_by_night = 0
        latitude = 0.0
        longitude = 0.0
    amenity_ids = []
