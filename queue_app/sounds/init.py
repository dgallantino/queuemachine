"""Build the sound map JSON from database state and static vocabulary."""

import json
from pathlib import Path
from typing import Any

from django.conf import settings

from queue_app import constants as const
from queue_app import models
from queue_app.sounds import paths
from queue_app.sounds.map import build_multi_lang_document, validate_lang_codes
from queue_app.sounds.vocabulary import LANGUAGE_LABELS, NUMBERS_BY_LANG, PHRASES


def _entry(text: str, lang_code: str, category: str) -> dict[str, str]:
    slug = paths.slugify_text(text)
    return {
        'text': text,
        'file': paths.fragment_relpath(lang_code, category, slug),
    }


def _collect_letters(lang_code: str, organization_id: str | None = None) -> dict[str, dict[str, str]]:
    """Queue characters used by services (e.g. A, B, C)."""
    qs = models.Service.objects.exclude(queue_char__isnull=True).exclude(queue_char='')
    if organization_id:
        qs = qs.filter(organization_id=organization_id)

    letters: dict[str, dict[str, str]] = {}
    for char in sorted({s.queue_char.upper() for s in qs if s.queue_char}):
        letters[char] = _entry(char, lang_code, paths.CATEGORY_LETTERS)
    return letters


def _collect_destinations(
    lang_code: str,
    organization_id: str | None = None,
) -> dict[str, dict[str, str]]:
    """Counter booth spoken names used as announcement destinations."""
    qs = models.CounterBooth.objects.all()
    if organization_id:
        qs = qs.filter(organization_id=organization_id)

    destinations: dict[str, dict[str, str]] = {}
    for booth in qs.order_by('spoken_name'):
        key = paths.slugify_text(booth.spoken_name)
        destinations[key] = _entry(booth.spoken_name, lang_code, paths.CATEGORY_DESTINATIONS)
    return destinations


def _collect_phrases(lang_code: str) -> dict[str, dict[str, str]]:
    phrases = PHRASES.get(lang_code, PHRASES[const.LANG.ID])
    return {
        key: _entry(text, lang_code, paths.CATEGORY_PHRASES)
        for key, text in phrases.items()
    }


def _collect_numbers(lang_code: str) -> dict[str, dict[str, dict[str, str]]]:
    number_sets = NUMBERS_BY_LANG.get(lang_code, NUMBERS_BY_LANG[const.LANG.ID])
    result: dict[str, dict[str, dict[str, str]]] = {}
    for group_name, values in number_sets.items():
        result[group_name] = {
            num_key: _entry(text, lang_code, paths.CATEGORY_NUMBERS)
            for num_key, text in values.items()
        }
    return result


def build_sound_map(
    lang_code: str | None = None,
    organization_id: str | None = None,
) -> dict[str, Any]:
    """Assemble the full sound map document for one language."""
    lang_code = lang_code or settings.LANGUAGE_CODE
    return {
        'language': LANGUAGE_LABELS.get(lang_code, lang_code),
        'lang_code': lang_code,
        'phrases': _collect_phrases(lang_code),
        'letters': _collect_letters(lang_code, organization_id),
        'numbers': _collect_numbers(lang_code),
        'destinations': _collect_destinations(lang_code, organization_id),
    }


def write_sound_map(
    map_path: Path | None = None,
    lang_codes: list[str] | None = None,
    organization_id: str | None = None,
    *,
    indent: int = 2,
) -> Path:
    """Write the sound map JSON to disk and ensure language audio dirs exist."""
    map_path = map_path or paths.default_map_path()
    audio_root = map_path.parent
    lang_codes = validate_lang_codes(lang_codes or [settings.LANGUAGE_CODE])

    lang_maps = {
        lang_code: build_sound_map(lang_code=lang_code, organization_id=organization_id)
        for lang_code in lang_codes
    }
    document = build_multi_lang_document(lang_maps)

    for lang_code in lang_codes:
        paths.lang_audio_dir(audio_root, lang_code).mkdir(parents=True, exist_ok=True)

    map_path.write_text(json.dumps(document, indent=indent, ensure_ascii=False) + '\n', encoding='utf-8')
    return map_path


def load_sound_map(map_path: Path | None = None) -> dict[str, Any]:
    """Load the sound map JSON document."""
    map_path = map_path or paths.default_map_path()
    return json.loads(map_path.read_text(encoding='utf-8'))
