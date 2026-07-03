"""Compose announcement audio from pre-generated fragments."""

import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Sequence

from queue_app.sounds import announcement, paths
from queue_app.sounds.init import load_sound_map
from queue_app.sounds.recipe import (
    ComposeRecipe,
    build_compose_recipe,
    build_queue_call_recipe,
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


def _ffmpeg_concat_escape(path: Path) -> str:
    """Escape a path for ffmpeg's concat demuxer list file."""
    return path.resolve().as_posix().replace("'", "'\\''")


def concatenate_wav_fragments(
    fragment_paths: Sequence[Path],
    output_path: Path,
) -> None:
    """Concatenate WAV files in order into ``output_path`` using ffmpeg."""
    if not fragment_paths:
        raise ValueError('At least one audio fragment is required')

    ffmpeg = shutil.which('ffmpeg')
    if ffmpeg is None:
        raise RuntimeError(
            'ffmpeg is required to compose announcement audio. '
            'Install ffmpeg and ensure it is on PATH.'
        )

    missing = [path for path in fragment_paths if not path.is_file()]
    if missing:
        raise FileNotFoundError(
            f'Audio fragment(s) not found: {", ".join(str(path) for path in missing)}'
        )

    output_path.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.NamedTemporaryFile(
        mode='w',
        suffix='.txt',
        delete=False,
        encoding='utf-8',
    ) as list_file:
        for path in fragment_paths:
            list_file.write(f"file '{_ffmpeg_concat_escape(path)}'\n")
        list_path = Path(list_file.name)

    try:
        result = subprocess.run(
            [
                ffmpeg,
                '-y',
                '-loglevel',
                'error',
                '-f',
                'concat',
                '-safe',
                '0',
                '-i',
                str(list_path),
                '-ar',
                '22050',
                '-ac',
                '1',
                str(output_path),
            ],
            capture_output=True,
            text=True,
            check=False,
        )
    finally:
        list_path.unlink(missing_ok=True)

    if result.returncode != 0:
        detail = (result.stderr or result.stdout or '').strip()
        raise RuntimeError(f'ffmpeg failed to compose announcement audio: {detail}')


def compose_announcement(
    fragment_keys: Sequence[str],
    map_path: Path | None = None,
    audio_root: Path | None = None,
    output_path: Path | None = None,
) -> tuple[Path, ComposeRecipe]:
    """Stitch fragments into one playable file following a compose recipe.

    Returns the output path and the recipe used. Fragments are concatenated
    in ``recipe.audio_sequence`` order via ffmpeg.
    """
    map_path = map_path or paths.default_map_path()
    audio_root = audio_root or paths.default_audio_root()
    sound_map = load_sound_map(map_path)
    recipe = build_compose_recipe(fragment_keys, sound_map=sound_map)
    fragment_paths = resolve_fragment_paths(fragment_keys, sound_map, audio_root)

    if output_path is None:
        suffix = paths.FRAGMENT_EXTENSION
        tmp = tempfile.NamedTemporaryFile(suffix=f'.{suffix}', delete=False)
        tmp.close()
        output_path = Path(tmp.name)

    concatenate_wav_fragments(fragment_paths, output_path)
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
