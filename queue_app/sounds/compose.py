"""Compose announcement audio from pre-generated fragments."""

import io
import wave
from pathlib import Path
from typing import Sequence

from queue_app import constants as const
from queue_app.sounds import announcement, paths
from queue_app.sounds.init import load_sound_map
from queue_app.sounds.map import get_lang_map
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


def concatenate_wav_fragments(fragment_paths: Sequence[Path]) -> bytes:
    """Concatenate WAV files in order and return the combined WAV as bytes."""
    if not fragment_paths:
        raise ValueError('At least one audio fragment is required')

    missing = [path for path in fragment_paths if not path.is_file()]
    if missing:
        raise FileNotFoundError(
            f'Audio fragment(s) not found: {", ".join(str(path) for path in missing)}'
        )

    frame_parts: list[bytes] = []
    nchannels = sampwidth = framerate = None
    comptype = compname = None

    for path in fragment_paths:
        with wave.open(str(path), 'rb') as wav_in:
            params = (
                wav_in.getnchannels(),
                wav_in.getsampwidth(),
                wav_in.getframerate(),
                wav_in.getcomptype(),
                wav_in.getcompname(),
            )
            if nchannels is None:
                nchannels, sampwidth, framerate, comptype, compname = params
            elif params != (nchannels, sampwidth, framerate, comptype, compname):
                raise ValueError(
                    f'Incompatible WAV format in {path}: expected '
                    f'{nchannels}ch/{sampwidth}byte/{framerate}Hz, '
                    f'got {params[0]}ch/{params[1]}byte/{params[2]}Hz'
                )
            frame_parts.append(wav_in.readframes(wav_in.getnframes()))

    buf = io.BytesIO()
    with wave.open(buf, 'wb') as wav_out:
        wav_out.setnchannels(nchannels)
        wav_out.setsampwidth(sampwidth)
        wav_out.setframerate(framerate)
        wav_out.setcomptype(comptype, compname)
        wav_out.writeframes(b''.join(frame_parts))

    return buf.getvalue()


def compose_announcement(
    fragment_keys: Sequence[str],
    lang_code: str,
    map_path: Path | None = None,
    audio_root: Path | None = None,
) -> tuple[bytes, ComposeRecipe]:
    """Stitch fragments into one playable WAV following a compose recipe.

    Returns the WAV bytes and the recipe used. Fragments are concatenated
    in ``recipe.audio_sequence`` order.
    """
    map_path = map_path or paths.default_map_path()
    audio_root = audio_root or paths.default_audio_root()
    document = load_sound_map(map_path)
    lang_map = get_lang_map(document, lang_code)
    recipe = build_compose_recipe(fragment_keys, lang_code=lang_code, sound_map=lang_map)
    fragment_paths = resolve_fragment_paths(fragment_keys, lang_map, audio_root)
    return concatenate_wav_fragments(fragment_paths), recipe


def compose_queue_call(
    queue_character: str,
    queue_number: int,
    destination_key: str,
    lang_code: str = const.LANG.ID,
    map_path: Path | None = None,
    audio_root: Path | None = None,
) -> tuple[bytes, ComposeRecipe]:
    """High-level helper: build the fragment list for a typical queue call."""
    map_path = map_path or paths.default_map_path()
    fragment_keys = announcement.compose_call_fragment_keys(
        queue_character,
        queue_number,
        destination_key,
        lang_code=lang_code,
    )
    return compose_announcement(
        fragment_keys,
        lang_code=lang_code,
        map_path=map_path,
        audio_root=audio_root,
    )
