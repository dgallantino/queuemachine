"""Tests for sound fragment generation progress reporting."""

from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import patch

from queue_app.sounds.generate import generate_fragments


class GenerateFragmentsProgressTests(TestCase):
    def test_on_progress_reports_start_and_done(self):
        events: list[tuple[str, str, int, int, str]] = []

        def on_progress(label, dest, index, total, phase):
            events.append((label, dest.name, index, total, phase))

        sound_map = {
            'lang_code': 'id',
            'phrases': {
                'queue_number': {'text': 'Nomor antrean', 'file': 'id/phrases_nomor_antrean.wav'},
            },
            'letters': {},
            'numbers': {},
            'destinations': {},
        }

        with TemporaryDirectory() as tmpdir:
            map_path = Path(tmpdir) / 'sound_map.json'
            audio_root = Path(tmpdir) / 'audio'
            map_path.write_text('{"lang_code":"id","phrases":{"queue_number":{"text":"Nomor antrean","file":"id/phrases_nomor_antrean.wav"}},"letters":{},"numbers":{},"destinations":{}}')

            with patch('queue_app.sounds.generate.get_default_provider') as get_provider:
                provider = get_provider.return_value
                written = generate_fragments(
                    map_path=map_path,
                    audio_root=audio_root,
                    on_progress=on_progress,
                )

            self.assertEqual(len(written), 1)
            provider.synthesize.assert_called_once()
            self.assertEqual(
                events,
                [
                    ('phrases.queue_number', 'phrases_nomor_antrean.wav', 1, 1, 'start'),
                    ('phrases.queue_number', 'phrases_nomor_antrean.wav', 1, 1, 'done'),
                ],
            )
