#!/usr/bin/python3
"""Define the Review model for file and database storage."""
import os
from models.base_model import BaseModel, Base

if os.getenv('HBNB_TYPE_STORAGE') == 'db':
    from sqlalchemy import Column, String, Integer, Float, ForeignKey


class Review(BaseModel, Base):
    """Represent a review using the selected storage engine."""

    if os.getenv('HBNB_TYPE_STORAGE') == 'db':
        __tablename__ = 'reviews'
        place_id = Column(
            String(60), ForeignKey('places.id'), nullable=False, default='')
        user_id = Column(
            String(60), ForeignKey('users.id'), nullable=False, default='')
        text = Column(String(1024), nullable=False, default='')
    else:
        place_id = ""
        user_id = ""
        text = ""
