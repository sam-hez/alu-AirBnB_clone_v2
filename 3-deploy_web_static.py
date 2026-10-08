#!/usr/bin/python3
"""Package and deploy the static website to both web servers."""
from datetime import datetime
from fabric.api import env, local, put, run, settings
from shlex import quote
import os


env.hosts = ['3.93.24.212', '54.89.145.102']


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


def do_deploy(archive_path):
    """Upload and activate an archive on the current Fabric host."""
    if not os.path.isfile(archive_path):
        return False
    filename = os.path.basename(archive_path)
    remote_archive = '/tmp/' + filename
    release = '/data/web_static/releases/' + os.path.splitext(filename)[0]
    try:
        with settings(warn_only=True, abort_exception=RuntimeError):
            if put(archive_path, remote_archive).failed:
                return False
            commands = [
                'mkdir -p {}'.format(quote(release)),
                'tar -xzf {} -C {} --strip-components=1'.format(
                    quote(remote_archive), quote(release)),
                'rm -f {}'.format(quote(remote_archive)),
                'rm -f /data/web_static/current',
                'ln -s {} /data/web_static/current'.format(quote(release))
            ]
            for command in commands:
                if run(command).failed:
                    return False
        return True
    except Exception:
        return False


def deploy():
    """Create an archive and return the result of deploying it."""
    archive_path = do_pack()
    if archive_path is None:
        return False
    return do_deploy(archive_path)
