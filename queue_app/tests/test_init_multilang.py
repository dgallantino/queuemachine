import pytest

from queue_app import constants as const
from queue_app.sounds.init import build_sound_map


@pytest.mark.django_db
def test_indonesian_phrases():
    sound_map = build_sound_map(lang_code=const.LANG.ID)
    assert sound_map['phrases']['queue_number']['text'] == 'Nomor antrean'
    assert sound_map['phrases']['queue_number']['file'] == 'id/phrases_nomor_antrean.wav'


@pytest.mark.django_db
def test_english_phrases():
    sound_map = build_sound_map(lang_code=const.LANG.EN)
    assert sound_map['phrases']['queue_number']['text'] == 'Queue number'
    assert sound_map['phrases']['queue_number']['file'] == 'en/phrases_queue_number.wav'


@pytest.mark.django_db
def test_english_numbers_include_teens_and_hundreds():
    sound_map = build_sound_map(lang_code=const.LANG.EN)
    assert sound_map['numbers']['special']['13']['text'] == 'thirteen'
    assert sound_map['numbers']['hundreds']['hundred']['text'] == 'hundred'
