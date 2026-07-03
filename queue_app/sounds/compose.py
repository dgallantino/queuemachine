"""Compose announcement audio from pre-generated fragments."""

import tempfile
from pathlib import Path
from typing import Sequence

from queue_app.sounds import announcement, paths
from queue_app.sounds.init import load_sound_map
from queue_app.sounds.recipe import (
    ComposeRecipe,
    build_compose_recipe,
    build_queue_call_recipe,
    recipe_fragment_abspaths,
    resolve_fragment_entries,
)


def resolve_fragment_paths(
    fragment_keys: Sequence[str],
    sound_map: dict,
    audio_root: Path | None = None,
) -> list[Path]:
    """Resolve logical fragment keys to absolute file paths.

    ``fragment_keys`` uses dotted paths into the map, e.g.
    ``phrases.queue_number``, ``letters.A``, ``numbers.ones.3``,
    ``destinations.konter_nomor_satu``.
    """
    audio_root = audio_root or paths.default_audio_root()
    entries = resolve_fragment_entries(fragment_keys, sound_map)
    return [paths.fragment_abspath(audio_root, entry['file']) for entry in entries]


def compose_announcement(
    fragment_keys: Sequence[str],
    map_path: Path | None = None,
    audio_root: Path | None = None,
    output_path: Path | None = None,
) -> tuple[Path, ComposeRecipe]:
    """Stitch fragments into one playable file following a compose recipe.

    Returns the output path and the recipe used. Concatenation logic will
    follow ``recipe.audio_sequence`` when implemented (pydub/ffmpeg).
    """
    map_path = map_path or paths.default_map_path()
    sound_map = load_sound_map(map_path)
    recipe = build_compose_recipe(fragment_keys, sound_map=sound_map)
    fragment_paths = recipe_fragment_abspaths(recipe, static_root=paths.default_audio_root().parent)

    if output_path is None:
        suffix = paths.FRAGMENT_EXTENSION
        tmp = tempfile.NamedTemporaryFile(suffix=f'.{suffix}', delete=False)
        tmp.close()
        output_path = Path(tmp.name)

    # TODO: concatenate ``fragment_paths`` following ``recipe.audio_sequence``.
    _ = fragment_paths
    output_path.touch(exist_ok=True)
    return output_path, recipe


def compose_queue_call(
    queue_character: str,
    queue_number: int,
    destination_key: str,
    map_path: Path | None = None,
    audio_root: Path | None = None,
    output_path: Path | None = None,
) -> tuple[Path, ComposeRecipe]:
    """High-level helper: build the fragment list for a typical queue call."""
    map_path = map_path or paths.default_map_path()
    fragment_keys = announcement.compose_call_fragment_keys(
        queue_character,
        queue_number,
        destination_key,
    )
    return compose_announcement(
        fragment_keys,
        map_path=map_path,
        audio_root=audio_root,
        output_path=output_path,
    )
