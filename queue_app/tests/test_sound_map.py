from django.test import SimpleTestCase

from queue_app import constants as const
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


class SoundMapHelpersTests(SimpleTestCase):
    def test_validate_lang_codes_accepts_supported(self):
        self.assertEqual(validate_lang_codes(['id', 'en']), ['id', 'en'])

    def test_validate_lang_codes_rejects_unsupported(self):
        with self.assertRaises(ValueError) as ctx:
            validate_lang_codes(['fr'])
        self.assertIn('fr', str(ctx.exception))

    def test_validate_lang_codes_requires_at_least_one(self):
        with self.assertRaises(ValueError):
            validate_lang_codes([])

    def test_iter_lang_maps_multi_lang(self):
        self.assertEqual(
            list(iter_lang_maps(MULTI_LANG_SOUND_MAP)),
            [('id', LEGACY_SOUND_MAP), ('en', MULTI_LANG_SOUND_MAP['languages']['en'])],
        )

    def test_iter_lang_maps_legacy(self):
        self.assertEqual(list(iter_lang_maps(LEGACY_SOUND_MAP)), [('id', LEGACY_SOUND_MAP)])

    def test_get_lang_map_multi_lang(self):
        self.assertEqual(get_lang_map(MULTI_LANG_SOUND_MAP, 'en')['lang_code'], 'en')

    def test_get_lang_map_legacy(self):
        self.assertEqual(get_lang_map(LEGACY_SOUND_MAP, 'id'), LEGACY_SOUND_MAP)

    def test_get_lang_map_missing_raises(self):
        with self.assertRaises(KeyError):
            get_lang_map(MULTI_LANG_SOUND_MAP, 'fr')

    def test_build_multi_lang_document(self):
        document = build_multi_lang_document({'id': LEGACY_SOUND_MAP})
        self.assertEqual(document, {'languages': {'id': LEGACY_SOUND_MAP}})
