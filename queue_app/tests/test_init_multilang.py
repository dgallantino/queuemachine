from django.test import TestCase

from queue_app import constants as const
from queue_app.sounds.init import build_sound_map


class BuildSoundMapTests(TestCase):
    def test_indonesian_phrases(self):
        sound_map = build_sound_map(lang_code=const.LANG.ID)
        self.assertEqual(sound_map['phrases']['queue_number']['text'], 'Nomor antrean')
        self.assertEqual(
            sound_map['phrases']['queue_number']['file'],
            'id/phrases_nomor_antrean.wav',
        )

    def test_english_phrases(self):
        sound_map = build_sound_map(lang_code=const.LANG.EN)
        self.assertEqual(sound_map['phrases']['queue_number']['text'], 'Queue number')
        self.assertEqual(
            sound_map['phrases']['queue_number']['file'],
            'en/phrases_queue_number.wav',
        )

    def test_english_numbers_include_teens_and_hundreds(self):
        sound_map = build_sound_map(lang_code=const.LANG.EN)
        self.assertEqual(sound_map['numbers']['special']['13']['text'], 'thirteen')
        self.assertEqual(sound_map['numbers']['hundreds']['hundred']['text'], 'hundred')
