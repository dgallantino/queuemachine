"""Local development settings — SQLite, debug enabled."""

import os

from queue_machine.settings import *  # noqa: F403

DEBUG = True

SECRET_KEY = os.getenv(
    'QUEUE_MACHINE_SECRET_KEY',
    'dev-insecure-secret-key-change-me',
)

ALLOWED_HOSTS = [
    host.strip()
    for host in os.getenv(
        'QUEUE_MACHINE_ALLOWED_HOSTS',
        'localhost,127.0.0.1',
    ).split(',')
    if host.strip()
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),  # noqa: F405
    }
}
