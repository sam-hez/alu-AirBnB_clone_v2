#!/usr/bin/python3
"""Select the storage engine using the HBNB_TYPE_STORAGE variable."""
import os

storage_t = os.getenv('HBNB_TYPE_STORAGE', 'file')
if storage_t == 'db':
    from models.engine.db_storage import DBStorage
    storage = DBStorage()
else:
    from models.engine.file_storage import FileStorage
    storage = FileStorage()
storage.reload()
