"""Queue-call announcement script and number decomposition rules."""

from queue_app import constants as const
from queue_app.sounds import paths

MAX_QUEUE_NUMBER = 999

CALL_TEMPLATE = (
    'queue_number',
    'letter',
    'number',
    'please_go_to',
    'destination',
)

PHRASE_KEYS = {
    'queue_number': 'phrases.queue_number',
    'please_go_to': 'phrases.please_go_to',
}


def destination_key_for_booth(spoken_name: str) -> str:
    """Map a booth spoken name to its destinations map key."""
    return paths.slugify_text(spoken_name)


def _number_fragment_keys_id(number: int) -> list[str]:
    """Decompose an integer queue number into Indonesian sound-map fragment keys."""
    if number <= 9:
        return [f'numbers.ones.{number}']

    if number == 10:
        return ['numbers.special.10']

    if number == 11:
        return ['numbers.special.11']

    if number <= 19:
        return [f'numbers.ones.{number - 10}', 'numbers.teens.belas']

    if number <= 99:
        keys = [f'numbers.tens.{(number // 10) * 10}']
        ones = number % 10
        if ones:
            keys.append(f'numbers.ones.{ones}')
        return keys

    if number == 100:
        return ['numbers.special.100']

    hundreds = (number // 100) * 100
    remainder = number % 100

    keys: list[str] = []
    if hundreds == 100:
        keys.append('numbers.special.100')
    else:
        keys.append(f'numbers.ones.{hundreds // 100}')
        keys.append('numbers.hundreds.ratus')

    if remainder:
        keys.extend(_number_fragment_keys_id(remainder))

    return keys


def _number_fragment_keys_en(number: int) -> list[str]:
    """Decompose an integer queue number into English sound-map fragment keys."""
    if number <= 9:
        return [f'numbers.ones.{number}']

    if number <= 19:
        return [f'numbers.special.{number}']

    if number <= 99:
        keys = [f'numbers.tens.{(number // 10) * 10}']
        ones = number % 10
        if ones:
            keys.append(f'numbers.ones.{ones}')
        return keys

    if number == 100:
        return ['numbers.special.100']

    hundreds = number // 100
    remainder = number % 100

    keys: list[str] = []
    if hundreds == 1:
        keys.append('numbers.special.100')
    else:
        keys.append(f'numbers.ones.{hundreds}')
        keys.append('numbers.hundreds.hundred')

    if remainder:
        keys.extend(_number_fragment_keys_en(remainder))

    return keys


def number_fragment_keys(number: int, lang_code: str = const.LANG.ID) -> list[str]:
    """Decompose an integer queue number into sound-map fragment keys (up to 999)."""
    if number < 0 or number > MAX_QUEUE_NUMBER:
        raise ValueError(f'queue number must be between 0 and {MAX_QUEUE_NUMBER}, got {number}')

    if lang_code == const.LANG.EN:
        return _number_fragment_keys_en(number)

    return _number_fragment_keys_id(number)


def compose_call_fragment_keys(
    queue_character: str,
    queue_number: int,
    destination_key: str,
    lang_code: str = const.LANG.ID,
) -> list[str]:
    """Return ordered dotted map keys for a full queue call announcement."""
    fragment_keys: list[str] = [
        PHRASE_KEYS['queue_number'],
        f'letters.{queue_character.upper()}',
    ]
    fragment_keys.extend(number_fragment_keys(queue_number, lang_code=lang_code))
    fragment_keys.append(PHRASE_KEYS['please_go_to'])
    fragment_keys.append(f'destinations.{destination_key}')
    return fragment_keys
