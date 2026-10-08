#!/usr/bin/python3
"""Package the static website with Fabric."""
from datetime import datetime
from fabric.api import local, settings
import os


def do_pack():
    """Create a timestamped archive and return its path, or None on failure."""
    archive_path = 'versions/web_static_{}.tgz'.format(
        datetime.now().strftime('%Y%m%d%H%M%S'))
    try:
        os.makedirs('versions', exist_ok=True)
        with settings(warn_only=True):
            result = local('tar -czf {} web_static'.format(archive_path))
        if result.failed:
            return None
        return archive_path
    except Exception:
        return None
