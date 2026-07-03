"""Generate individual sound fragments from the sound map via TTS providers."""

from collections.abc import Callable
from pathlib import Path
from typing import Iterable, Literal

from queue_app.sounds import paths
from queue_app.sounds.init import load_sound_map
from queue_app.sounds.providers.base import TTSProvider, get_default_provider

ProgressPhase = Literal['start', 'done']
ProgressCallback = Callable[[str, Path, int, int, ProgressPhase], None]


def iter_map_fragments(sound_map: dict) -> Iterable[tuple[str, dict]]:
    """Yield ``(category, entry)`` pairs for every fragment listed in the map."""
    lang_code = sound_map['lang_code']

    for key, entry in sound_map.get('phrases', {}).items():
        yield f'phrases.{key}', entry

    for key, entry in sound_map.get('letters', {}).items():
        yield f'letters.{key}', entry

    for group_name, group in sound_map.get('numbers', {}).items():
        for key, entry in group.items():
            yield f'numbers.{group_name}.{key}', entry

    for key, entry in sound_map.get('destinations', {}).items():
        yield f'destinations.{key}', entry

    # lang_code is available on the map but not yielded as a fragment category.
    _ = lang_code


def generate_fragments(
    map_path: Path | None = None,
    audio_root: Path | None = None,
    provider: TTSProvider | None = None,
    *,
    dry_run: bool = False,
    on_progress: ProgressCallback | None = None,
) -> list[Path]:
    """Generate WAV fragments for every entry in the sound map.

    Returns paths that would be (or were) written. Actual TTS calls are delegated
    to ``provider``; the default provider is a no-op stub until configured.

    ``on_progress`` is called as ``(label, dest, index, total, phase)`` where
    ``phase`` is ``'start'`` before synthesis and ``'done'`` after.
    """
    map_path = map_path or paths.default_map_path()
    audio_root = audio_root or paths.default_audio_root()
    sound_map = load_sound_map(map_path)
    provider = provider or get_default_provider()

    fragments = list(iter_map_fragments(sound_map))
    total = len(fragments)
    written: list[Path] = []

    for index, (label, entry) in enumerate(fragments, start=1):
        dest = paths.fragment_abspath(audio_root, entry['file'])
        dest.parent.mkdir(parents=True, exist_ok=True)

        if on_progress:
            on_progress(label, dest, index, total, 'start')

        if dry_run:
            written.append(dest)
            if on_progress:
                on_progress(label, dest, index, total, 'done')
            continue

        provider.synthesize(text=entry['text'], output_path=dest, lang_code=sound_map['lang_code'])
        written.append(dest)

        if on_progress:
            on_progress(label, dest, index, total, 'done')

    return written
