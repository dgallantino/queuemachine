"""Locked Indonesian queue-call announcement script and number decomposition rules."""

from queue_app.sounds import paths

MAX_QUEUE_NUMBER = 999

# Ordered roles in a queue call (Phase 1: Indonesian only).
CALL_TEMPLATE_ID = (
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


def number_fragment_keys(number: int) -> list[str]:
    """Decompose an integer queue number into sound-map fragment keys (id, up to 999).

    Uses formal Indonesian composition:
    - 13 -> ones.3 + teens.belas
    - 25 -> tens.20 + ones.5
    - 115 -> special.100 + ones.5 + teens.belas
    - 999 -> ones.9 + hundreds.ratus + tens.90 + ones.9
    """
    if number < 0 or number > MAX_QUEUE_NUMBER:
        raise ValueError(f'queue number must be between 0 and {MAX_QUEUE_NUMBER}, got {number}')

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
        keys.extend(number_fragment_keys(remainder))

    return keys


def compose_call_fragment_keys(
    queue_character: str,
    queue_number: int,
    destination_key: str,
) -> list[str]:
    """Return ordered dotted map keys for a full queue call announcement."""
    fragment_keys: list[str] = [
        PHRASE_KEYS['queue_number'],
        f'letters.{queue_character.upper()}',
    ]
    fragment_keys.extend(number_fragment_keys(queue_number))
    fragment_keys.append(PHRASE_KEYS['please_go_to'])
    fragment_keys.append(f'destinations.{destination_key}')
    return fragment_keys
