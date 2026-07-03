"""Compose recipe: testable plan for stitching announcement fragments."""

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Sequence

from queue_app.sounds import announcement, paths
from queue_app.sounds.init import load_sound_map

PLEASE_GO_TO_KEY = announcement.PHRASE_KEYS['please_go_to']


@dataclass(frozen=True)
class ComposeRecipe:
    """Ordered plan for concatenating pre-generated WAV fragments."""

    text: str
    language: str
    audio_sequence: list[str]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def recipe_audio_relpath(map_file_relpath: str) -> str:
    """Return recipe-style path, e.g. ``audio/id/phrases_nomor_antrean.wav``."""
    return f'audio/{map_file_relpath}'


def resolve_fragment_entries(
    fragment_keys: Sequence[str],
    sound_map: dict,
) -> list[dict[str, str]]:
    """Resolve dotted map keys to ``text`` and ``file`` entries from the sound map."""
    entries: list[dict[str, str]] = []
    for key in fragment_keys:
        node = sound_map
        for part in key.split('.'):
            node = node[part]
        entries.append({'text': node['text'], 'file': node['file']})
    return entries


def build_recipe_text(fragment_keys: Sequence[str], entries: Sequence[dict[str, str]]) -> str:
    """Build human-readable announcement text from ordered fragment entries."""
    texts = [entry['text'] for entry in entries]

    if PLEASE_GO_TO_KEY in fragment_keys:
        split_at = fragment_keys.index(PLEASE_GO_TO_KEY)
        before = ' '.join(texts[:split_at])
        after = ' '.join(texts[split_at:])
        return f'{before}, {after}.'

    return f'{" ".join(texts)}.'


def build_compose_recipe(
    fragment_keys: Sequence[str],
    sound_map: dict | None = None,
    map_path: Path | None = None,
) -> ComposeRecipe:
    """Build a compose recipe from fragment keys and the sound map."""
    if sound_map is None:
        sound_map = load_sound_map(map_path)

    entries = resolve_fragment_entries(fragment_keys, sound_map)
    return ComposeRecipe(
        text=build_recipe_text(fragment_keys, entries),
        language=sound_map['lang_code'],
        audio_sequence=[recipe_audio_relpath(entry['file']) for entry in entries],
    )


def build_queue_call_recipe(
    queue_character: str,
    queue_number: int,
    destination_key: str,
    sound_map: dict | None = None,
    map_path: Path | None = None,
) -> ComposeRecipe:
    """Build a compose recipe for a standard queue call announcement."""
    fragment_keys = announcement.compose_call_fragment_keys(
        queue_character,
        queue_number,
        destination_key,
    )
    return build_compose_recipe(fragment_keys, sound_map=sound_map, map_path=map_path)


def recipe_fragment_abspaths(
    recipe: ComposeRecipe,
    static_root: Path | None = None,
) -> list[Path]:
    """Resolve recipe ``audio_sequence`` paths to absolute filesystem paths."""
    static_root = static_root or paths.default_audio_root().parent
    return [static_root / relpath for relpath in recipe.audio_sequence]
