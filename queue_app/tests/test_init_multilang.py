import pytest

from queue_app import constants as const
from queue_app.sounds.init import build_sound_map


@pytest.mark.django_db
def test_indonesian_phrases():
    sound_map = build_sound_map(lang_codes=[const.LANG.ID])
    lang_map = sound_map['languages']['id']
    assert lang_map['phrases']['queue_number']['text'] == 'Nomor antrean'
    assert lang_map['phrases']['queue_number']['file'] == 'id/phrases_nomor_antrean.wav'


@pytest.mark.django_db
def test_english_phrases():
    sound_map = build_sound_map(lang_codes=[const.LANG.EN])
    lang_map = sound_map['languages']['en']
    assert lang_map['phrases']['queue_number']['text'] == 'Queue number'
    assert lang_map['phrases']['queue_number']['file'] == 'en/phrases_queue_number.wav'


@pytest.mark.django_db
def test_english_numbers_include_teens_and_hundreds():
    sound_map = build_sound_map(lang_codes=[const.LANG.EN])
    lang_map = sound_map['languages']['en']
    assert lang_map['numbers']['special']['13']['text'] == 'thirteen'
    assert lang_map['numbers']['hundreds']['hundred']['text'] == 'hundred'


@pytest.mark.django_db
def test_single_language_uses_multi_lang_structure():
    sound_map = build_sound_map(lang_codes=[const.LANG.ID])
    assert set(sound_map.keys()) == {'languages'}
    assert set(sound_map['languages'].keys()) == {const.LANG.ID}
