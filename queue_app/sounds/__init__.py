"""Queue announcement sound assets: map, generation, and composition."""

from queue_app.sounds.compose import compose_announcement, compose_queue_call
from queue_app.sounds.generate import generate_fragments
from queue_app.sounds.init import build_sound_map, write_sound_map
from queue_app.sounds.paths import (
    default_audio_root,
    default_map_path,
    fragment_filename,
    fragment_relpath,
)
from queue_app.sounds.recipe import (
    ComposeRecipe,
    build_compose_recipe,
    build_queue_call_recipe,
)

__all__ = [
    'build_sound_map',
    'write_sound_map',
    'generate_fragments',
    'compose_announcement',
    'compose_queue_call',
    'ComposeRecipe',
    'build_compose_recipe',
    'build_queue_call_recipe',
    'default_audio_root',
    'default_map_path',
    'fragment_filename',
    'fragment_relpath',
]
