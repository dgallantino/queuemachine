import pytest

from queue_app.sounds.map import (
    build_multi_lang_document,
    get_lang_map,
    iter_lang_maps,
    validate_lang_codes,
)


LEGACY_SOUND_MAP = {
    'language': 'Bahasa Indonesia',
    'lang_code': 'id',
    'phrases': {},
    'letters': {},
    'numbers': {},
    'destinations': {},
}

MULTI_LANG_SOUND_MAP = {
    'languages': {
        'id': LEGACY_SOUND_MAP,
        'en': {
            'language': 'English',
            'lang_code': 'en',
            'phrases': {},
            'letters': {},
            'numbers': {},
            'destinations': {},
        },
    },
}


def test_validate_lang_codes_accepts_supported():
    assert validate_lang_codes(['id', 'en']) == ['id', 'en']


def test_validate_lang_codes_rejects_unsupported():
    with pytest.raises(ValueError, match='fr'):
        validate_lang_codes(['fr'])


def test_validate_lang_codes_requires_at_least_one():
    with pytest.raises(ValueError):
        validate_lang_codes([])


def test_iter_lang_maps_multi_lang():
    assert list(iter_lang_maps(MULTI_LANG_SOUND_MAP)) == [
        ('id', LEGACY_SOUND_MAP),
        ('en', MULTI_LANG_SOUND_MAP['languages']['en']),
    ]


def test_iter_lang_maps_legacy():
    assert list(iter_lang_maps(LEGACY_SOUND_MAP)) == [('id', LEGACY_SOUND_MAP)]


def test_get_lang_map_multi_lang():
    assert get_lang_map(MULTI_LANG_SOUND_MAP, 'en')['lang_code'] == 'en'


def test_get_lang_map_legacy():
    assert get_lang_map(LEGACY_SOUND_MAP, 'id') == LEGACY_SOUND_MAP


def test_get_lang_map_missing_raises():
    with pytest.raises(KeyError):
        get_lang_map(MULTI_LANG_SOUND_MAP, 'fr')


def test_build_multi_lang_document():
    document = build_multi_lang_document({'id': LEGACY_SOUND_MAP})
    assert document == {'languages': {'id': LEGACY_SOUND_MAP}}
