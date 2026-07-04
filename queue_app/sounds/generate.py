"""Generate individual sound fragments from the sound map via TTS providers."""

from collections.abc import Callable
from pathlib import Path
from typing import Iterable, Literal

from queue_app.sounds import paths
from queue_app.sounds.init import load_sound_map
from queue_app.sounds.map import iter_lang_maps
from queue_app.sounds.providers.base import TTSProvider, get_default_provider

ProgressPhase = Literal['start', 'done', 'skip']
ProgressCallback = Callable[[str, Path, int, int, ProgressPhase], None]


def iter_lang_map_fragments(lang_code: str, sound_map: dict) -> Iterable[tuple[str, dict]]:
    """Yield ``(label, entry)`` pairs for every fragment in one language section."""
    for key, entry in sound_map.get('phrases', {}).items():
        yield f'{lang_code}.phrases.{key}', entry

    for key, entry in sound_map.get('letters', {}).items():
        yield f'{lang_code}.letters.{key}', entry

    for group_name, group in sound_map.get('numbers', {}).items():
        for key, entry in group.items():
            yield f'{lang_code}.numbers.{group_name}.{key}', entry

    for key, entry in sound_map.get('destinations', {}).items():
        yield f'{lang_code}.destinations.{key}', entry


def iter_map_fragments(document: dict) -> Iterable[tuple[str, dict, str]]:
    """Yield ``(label, entry, lang_code)`` for every fragment across all languages."""
    for lang_code, lang_map in iter_lang_maps(document):
        for label, entry in iter_lang_map_fragments(lang_code, lang_map):
            yield label, entry, lang_code


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
    document = load_sound_map(map_path)
    provider = provider or get_default_provider()

    fragments = list(iter_map_fragments(document))
    total = len(fragments)
    written: list[Path] = []

    for index, (label, entry, lang_code) in enumerate(fragments, start=1):
        dest = paths.fragment_abspath(audio_root, entry['file'])

        if dest.is_file():
            if on_progress:
                on_progress(label, dest, index, total, 'skip')
            continue

        dest.parent.mkdir(parents=True, exist_ok=True)

        if on_progress:
            on_progress(label, dest, index, total, 'start')

        if dry_run:
            written.append(dest)
            if on_progress:
                on_progress(label, dest, index, total, 'done')
            continue

        provider.synthesize(text=entry['text'], output_path=dest, lang_code=lang_code)
        written.append(dest)

        if on_progress:
            on_progress(label, dest, index, total, 'done')

    return written
