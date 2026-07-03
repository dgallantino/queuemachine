"""Static phrase and number vocabulary per language.

These defaults seed the sound map during ``init``. Phase 1 locks Indonesian (id)
announcement atoms; English entries are deferred until Phase 2.
"""

from queue_app import constants as const

# Fixed announcement phrases for the locked id call template:
# Nomor antrean -> letter -> number -> silakan menuju -> destination
PHRASES = {
    const.LANG.ID: {
        'queue_number': 'Nomor antrean',
        'please_go_to': 'silakan menuju',
    },
    # deferred — phase 2
    const.LANG.EN: {
        'queue_number': 'Queue number',
        'please_go_to': 'please go to',
    },
}

LANGUAGE_LABELS = {
    const.LANG.ID: 'Bahasa Indonesia',
    const.LANG.EN: 'English',
}

# Indonesian number atoms for fragment generation (composed at runtime up to 999).
ID_ONES = {
    '1': 'satu',
    '2': 'dua',
    '3': 'tiga',
    '4': 'empat',
    '5': 'lima',
    '6': 'enam',
    '7': 'tujuh',
    '8': 'delapan',
    '9': 'sembilan',
}

ID_SPECIAL = {
    '10': 'sepuluh',
    '11': 'sebelas',
    '100': 'seratus',
    '1000': 'seribu',
}

ID_TENS = {
    '20': 'dua puluh',
    '30': 'tiga puluh',
    '40': 'empat puluh',
    '50': 'lima puluh',
    '60': 'enam puluh',
    '70': 'tujuh puluh',
    '80': 'delapan puluh',
    '90': 'sembilan puluh',
}

ID_TEENS = {
    'belas': 'belas',
}

ID_HUNDREDS = {
    'ratus': 'ratus',
}

# deferred — phase 2
EN_ONES = {str(i): name for i, name in enumerate(
    ['zero', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine'],
    start=0,
) if i > 0}

EN_SPECIAL = {
    '10': 'ten',
    '11': 'eleven',
    '12': 'twelve',
    '100': 'one hundred',
    '1000': 'one thousand',
}

EN_TENS = {
    '20': 'twenty',
    '30': 'thirty',
    '40': 'forty',
    '50': 'fifty',
    '60': 'sixty',
    '70': 'seventy',
    '80': 'eighty',
    '90': 'ninety',
}

NUMBERS_BY_LANG = {
    const.LANG.ID: {
        'ones': ID_ONES,
        'special': ID_SPECIAL,
        'tens': ID_TENS,
        'teens': ID_TEENS,
        'hundreds': ID_HUNDREDS,
    },
    # deferred — phase 2
    const.LANG.EN: {'ones': EN_ONES, 'special': EN_SPECIAL, 'tens': EN_TENS},
}
