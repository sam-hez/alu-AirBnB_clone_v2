#!/usr/bin/python3
"""Define the State model for file and database storage."""
import os
from models.base_model import BaseModel, Base

if os.getenv('HBNB_TYPE_STORAGE') == 'db':
    from sqlalchemy import Column, String, Integer, Float, ForeignKey


class State(BaseModel, Base):
    """Represent a state using the selected storage engine."""

    if os.getenv('HBNB_TYPE_STORAGE') == 'db':
        __tablename__ = 'states'
        name = Column(String(128), nullable=False, default='')
    else:
        name = ""
