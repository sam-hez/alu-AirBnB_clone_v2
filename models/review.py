#!/usr/bin/python3
"""Define the Review model for file and database storage."""
import os
from models.base_model import BaseModel, Base

if os.getenv('HBNB_TYPE_STORAGE') == 'db':
    from sqlalchemy import Column, String, ForeignKey


class Review(BaseModel, Base):
    """Represent a review using the selected storage engine."""

    if os.getenv('HBNB_TYPE_STORAGE') == 'db':
        __tablename__ = 'reviews'
        place_id = Column(
            String(60), ForeignKey('places.id'), nullable=False)
        user_id = Column(
            String(60), ForeignKey('users.id'), nullable=False)
        text = Column(String(1024), nullable=False)
    else:
        place_id = ""
        user_id = ""
        text = ""
