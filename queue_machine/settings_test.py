"""Test settings — SQLite test database, debug enabled."""

import os

from queue_machine.settings import *  # noqa: F403

DEBUG = True

SECRET_KEY = os.getenv(
    'QUEUE_MACHINE_SECRET_KEY',
    'test-insecure-secret-key',
)

ALLOWED_HOSTS = [
    host.strip()
    for host in os.getenv(
        'QUEUE_MACHINE_ALLOWED_HOSTS',
        'localhost,127.0.0.1,testserver',
    ).split(',')
    if host.strip()
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'test_db.sqlite3'),  # noqa: F405
    }
}
