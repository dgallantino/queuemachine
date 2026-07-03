"""Filesystem paths and naming conventions for sound fragments."""

import re
from pathlib import Path

from django.conf import settings

CATEGORY_PHRASES = 'phrases'
CATEGORY_LETTERS = 'letters'
CATEGORY_NUMBERS = 'numbers'
CATEGORY_DESTINATIONS = 'destinations'

FRAGMENT_EXTENSION = 'wav'


def slugify_text(text: str) -> str:
    """Turn spoken text into a safe filename segment."""
    slug = text.lower().strip()
    slug = re.sub(r'[^\w\s-]', '', slug, flags=re.UNICODE)
    slug = re.sub(r'[\s_-]+', '_', slug)
    return slug or 'unknown'


def fragment_filename(category: str, slug: str, extension: str = FRAGMENT_EXTENSION) -> str:
    """Return a flat fragment filename, e.g. ``phrases_nomor_antrean.wav``."""
    return f'{category}_{slug}.{extension}'


def fragment_relpath(
    lang_code: str,
    category: str,
    slug: str,
    extension: str = FRAGMENT_EXTENSION,
) -> str:
    """Return a map-relative path, e.g. ``id/phrases_nomor_antrean.wav``."""
    return f'{lang_code}/{fragment_filename(category, slug, extension)}'


def default_audio_root() -> Path:
    """Root directory where generated fragments are stored."""
    return Path(settings.BASE_DIR) / 'queue_app' / 'static' / 'queue_app' / 'audio'


def default_map_path() -> Path:
    """Default location for the sound map JSON document."""
    return default_audio_root() / 'sound_map.json'


def fragment_abspath(audio_root: Path, relpath: str) -> Path:
    """Resolve a map ``file`` entry to an absolute path."""
    return audio_root / relpath


def lang_audio_dir(audio_root: Path, lang_code: str) -> Path:
    """Directory for one language's fragments."""
    return audio_root / lang_code
