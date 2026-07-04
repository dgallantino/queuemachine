"""Multi-language sound map document helpers."""

from collections.abc import Iterable
from typing import Any

from queue_app import constants as const

SUPPORTED_LANGS = frozenset({const.LANG.ID, const.LANG.EN})


def validate_lang_codes(lang_codes: list[str]) -> list[str]:
    """Return validated language codes, raising ``ValueError`` for unsupported codes."""
    if not lang_codes:
        raise ValueError('At least one language code is required')

    invalid = [code for code in lang_codes if code not in SUPPORTED_LANGS]
    if invalid:
        supported = ', '.join(sorted(SUPPORTED_LANGS))
        invalid_list = ', '.join(invalid)
        raise ValueError(f'Unsupported language code(s): {invalid_list}. Supported: {supported}')

    return lang_codes


def is_multi_lang_document(document: dict[str, Any]) -> bool:
    """Return True when the document uses the combined ``languages`` wrapper."""
    return 'languages' in document


def iter_lang_maps(document: dict[str, Any]) -> Iterable[tuple[str, dict[str, Any]]]:
    """Yield ``(lang_code, lang_map)`` pairs from a sound map document.

    Legacy single-language documents (flat top-level ``lang_code``) are yielded
    as a single pair.
    """
    if is_multi_lang_document(document):
        for lang_code, lang_map in document['languages'].items():
            yield lang_code, lang_map
        return

    yield document['lang_code'], document


def get_lang_map(document: dict[str, Any], lang_code: str) -> dict[str, Any]:
    """Return the language section for ``lang_code``."""
    if is_multi_lang_document(document):
        try:
            return document['languages'][lang_code]
        except KeyError as exc:
            raise KeyError(f'Language {lang_code!r} not found in sound map') from exc

    if document.get('lang_code') == lang_code:
        return document

    raise KeyError(f'Language {lang_code!r} not found in sound map')


def build_multi_lang_document(lang_maps: dict[str, dict[str, Any]]) -> dict[str, Any]:
    """Wrap per-language maps in the combined document format."""
    return {'languages': lang_maps}
