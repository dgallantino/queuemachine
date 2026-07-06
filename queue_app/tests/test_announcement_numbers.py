import pytest

from queue_app import constants as const
from queue_app.sounds.announcement import compose_call_fragment_keys, number_fragment_keys


def test_teens():
    assert number_fragment_keys(13) == ['numbers.ones.3', 'numbers.teens.belas']


def test_tens_and_ones():
    assert number_fragment_keys(25) == ['numbers.tens.20', 'numbers.ones.5']


def test_ninety_nine():
    assert number_fragment_keys(99) == ['numbers.tens.90', 'numbers.ones.9']


def test_one_hundred():
    assert number_fragment_keys(100) == ['numbers.special.100']


def test_one_hundred_fifteen():
    assert number_fragment_keys(115) == [
        'numbers.special.100',
        'numbers.ones.5',
        'numbers.teens.belas',
    ]


def test_one_hundred_twenty_five():
    assert number_fragment_keys(125) == [
        'numbers.special.100',
        'numbers.tens.20',
        'numbers.ones.5',
    ]


def test_two_hundred():
    assert number_fragment_keys(200) == ['numbers.ones.2', 'numbers.hundreds.ratus']


def test_two_hundred_fifty():
    assert number_fragment_keys(250) == [
        'numbers.ones.2',
        'numbers.hundreds.ratus',
        'numbers.tens.50',
    ]


def test_nine_hundred_ninety_nine():
    assert number_fragment_keys(999) == [
        'numbers.ones.9',
        'numbers.hundreds.ratus',
        'numbers.tens.90',
        'numbers.ones.9',
    ]


def test_rejects_out_of_range():
    with pytest.raises(ValueError):
        number_fragment_keys(1000)


def test_english_teens():
    assert number_fragment_keys(13, lang_code=const.LANG.EN) == ['numbers.special.13']


def test_english_tens_and_ones():
    assert number_fragment_keys(25, lang_code=const.LANG.EN) == [
        'numbers.tens.20',
        'numbers.ones.5',
    ]


def test_english_one_hundred_fifteen():
    assert number_fragment_keys(115, lang_code=const.LANG.EN) == [
        'numbers.special.100',
        'numbers.special.15',
    ]


def test_english_two_hundred_fifty():
    assert number_fragment_keys(250, lang_code=const.LANG.EN) == [
        'numbers.ones.2',
        'numbers.hundreds.hundred',
        'numbers.tens.50',
    ]


def test_english_nine_hundred_ninety_nine():
    assert number_fragment_keys(999, lang_code=const.LANG.EN) == [
        'numbers.ones.9',
        'numbers.hundreds.hundred',
        'numbers.tens.90',
        'numbers.ones.9',
    ]


def test_full_call_a25():
    assert compose_call_fragment_keys('A', 25, 'konter_farmasi') == [
        'phrases.queue_number',
        'letters.A',
        'numbers.tens.20',
        'numbers.ones.5',
        'phrases.please_go_to',
        'destinations.konter_farmasi',
    ]


def test_full_call_en_a25():
    assert compose_call_fragment_keys('A', 25, 'counter_one', lang_code=const.LANG.EN) == [
        'phrases.queue_number',
        'letters.A',
        'numbers.tens.20',
        'numbers.ones.5',
        'phrases.please_go_to',
        'destinations.counter_one',
    ]
