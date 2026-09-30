#!/usr/bin/python3
"""Define the Place model for file and database storage."""
import os
from models.base_model import BaseModel, Base

if os.getenv('HBNB_TYPE_STORAGE') == 'db':
    from sqlalchemy import Column, String, Integer, Float, ForeignKey, Table
    from sqlalchemy.orm import relationship

    place_amenity = Table(
        'place_amenity', Base.metadata,
        Column('place_id', String(60), ForeignKey('places.id'),
               primary_key=True, nullable=False),
        Column('amenity_id', String(60), ForeignKey('amenities.id'),
               primary_key=True, nullable=False))


class Place(BaseModel, Base):
    """Represent a place using the selected storage engine."""

    if os.getenv('HBNB_TYPE_STORAGE') == 'db':
        __tablename__ = 'places'
        city_id = Column(
            String(60), ForeignKey('cities.id'), nullable=False)
        user_id = Column(
            String(60), ForeignKey('users.id'), nullable=False)
        name = Column(String(128), nullable=False)
        description = Column(String(1024))
        number_rooms = Column(Integer, nullable=False, default=0)
        number_bathrooms = Column(Integer, nullable=False, default=0)
        max_guest = Column(Integer, nullable=False, default=0)
        price_by_night = Column(Integer, nullable=False, default=0)
        latitude = Column(Float)
        longitude = Column(Float)
        reviews = relationship('Review', backref='place',
                               cascade='all, delete-orphan')
        amenities = relationship(
            'Amenity', secondary=place_amenity, viewonly=False,
            back_populates='place_amenities')
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

        @property
        def reviews(self):
            """Return stored reviews belonging to this place."""
            from models import storage
            from models.review import Review
            return [review for review in storage.all(Review).values()
                    if review.place_id == self.id]

        @property
        def amenities(self):
            """Return stored amenities linked to this place."""
            from models import storage
            from models.amenity import Amenity
            return [amenity for amenity in storage.all(Amenity).values()
                    if amenity.id in self.amenity_ids]

        @amenities.setter
        def amenities(self, amenity):
            """Add an amenity ID without sharing lists between places."""
            from models.amenity import Amenity
            if isinstance(amenity, Amenity):
                self.amenity_ids = list(self.amenity_ids)
                if amenity.id not in self.amenity_ids:
                    self.amenity_ids.append(amenity.id)
