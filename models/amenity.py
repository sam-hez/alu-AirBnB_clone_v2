#!/usr/bin/python3
"""Define the Amenity model for file and database storage."""
import os
from models.base_model import BaseModel, Base

if os.getenv('HBNB_TYPE_STORAGE') == 'db':
    from sqlalchemy import Column, String
    from sqlalchemy.orm import relationship


class Amenity(BaseModel, Base):
    """Represent a amenity using the selected storage engine."""

    if os.getenv('HBNB_TYPE_STORAGE') == 'db':
        __tablename__ = 'amenities'
        name = Column(String(128), nullable=False)
        place_amenities = relationship(
            'Place', secondary='place_amenity', back_populates='amenities')
    else:
        name = ""
