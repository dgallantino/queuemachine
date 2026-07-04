from django.test import SimpleTestCase

from queue_app.sounds.recipe import build_queue_call_recipe


FIXTURE_SOUND_MAP = {
    'language': 'Bahasa Indonesia',
    'lang_code': 'id',
    'phrases': {
        'queue_number': {
            'text': 'Nomor antrean',
            'file': 'id/phrases_nomor_antrean.wav',
        },
        'please_go_to': {
            'text': 'silakan menuju',
            'file': 'id/phrases_silakan_menuju.wav',
        },
    },
    'letters': {
        'A': {
            'text': 'A',
            'file': 'id/letters_a.wav',
        },
    },
    'numbers': {
        'ones': {
            '3': {'text': 'tiga', 'file': 'id/numbers_tiga.wav'},
        },
        'special': {
            '100': {'text': 'seratus', 'file': 'id/numbers_seratus.wav'},
        },
        'tens': {
            '20': {'text': 'dua puluh', 'file': 'id/numbers_dua_puluh.wav'},
        },
        'teens': {
            'belas': {'text': 'belas', 'file': 'id/numbers_belas.wav'},
        },
        'hundreds': {
            'ratus': {'text': 'ratus', 'file': 'id/numbers_ratus.wav'},
        },
    },
    'destinations': {
        'konter_satu': {
            'text': 'konter satu',
            'file': 'id/destinations_konter_satu.wav',
        },
    },
}


class ComposeRecipeTests(SimpleTestCase):
    def test_queue_call_a123_konter_satu(self):
        recipe = build_queue_call_recipe(
            'A',
            123,
            'konter_satu',
            lang_code='id',
            sound_map=FIXTURE_SOUND_MAP,
        )

        self.assertEqual(
            recipe.to_dict(),
            {
                'text': 'Nomor antrean A seratus dua puluh tiga, silakan menuju konter satu.',
                'language': 'id',
                'audio_sequence': [
                    'audio/id/phrases_nomor_antrean.wav',
                    'audio/id/letters_a.wav',
                    'audio/id/numbers_seratus.wav',
                    'audio/id/numbers_dua_puluh.wav',
                    'audio/id/numbers_tiga.wav',
                    'audio/id/phrases_silakan_menuju.wav',
                    'audio/id/destinations_konter_satu.wav',
                ],
            },
        )
