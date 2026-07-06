import pytest

from queue_app.sounds.map import (
    build_multi_lang_document,
    get_lang_map,
    iter_lang_maps,
    validate_lang_codes,
)


MULTI_LANG_SOUND_MAP = {
    'languages': {
        'id': {
            'language': 'Bahasa Indonesia',
            'lang_code': 'id',
            'phrases': {},
            'letters': {},
            'numbers': {},
            'destinations': {},
        },
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


def test_iter_lang_maps():
    assert list(iter_lang_maps(MULTI_LANG_SOUND_MAP)) == [
        ('id', MULTI_LANG_SOUND_MAP['languages']['id']),
        ('en', MULTI_LANG_SOUND_MAP['languages']['en']),
    ]


def test_get_lang_map():
    assert get_lang_map(MULTI_LANG_SOUND_MAP, 'en')['lang_code'] == 'en'


def test_get_lang_map_missing_raises():
    with pytest.raises(KeyError):
        get_lang_map(MULTI_LANG_SOUND_MAP, 'fr')


def test_build_multi_lang_document():
    id_map = MULTI_LANG_SOUND_MAP['languages']['id']
    document = build_multi_lang_document({'id': id_map})
    assert document == {'languages': {'id': id_map}}
