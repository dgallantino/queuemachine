"""Tests for sound fragment generation progress reporting."""

import json
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
                    ('id.phrases.queue_number', 'phrases_nomor_antrean.wav', 1, 1, 'start'),
                    ('id.phrases.queue_number', 'phrases_nomor_antrean.wav', 1, 1, 'done'),
                ],
            )

    def test_generates_fragments_for_all_languages(self):
        document = {
            'languages': {
                'id': {
                    'lang_code': 'id',
                    'phrases': {
                        'queue_number': {
                            'text': 'Nomor antrean',
                            'file': 'id/phrases_nomor_antrean.wav',
                        },
                    },
                    'letters': {},
                    'numbers': {},
                    'destinations': {},
                },
                'en': {
                    'lang_code': 'en',
                    'phrases': {
                        'queue_number': {
                            'text': 'Queue number',
                            'file': 'en/phrases_queue_number.wav',
                        },
                    },
                    'letters': {},
                    'numbers': {},
                    'destinations': {},
                },
            },
        }

        with TemporaryDirectory() as tmpdir:
            map_path = Path(tmpdir) / 'sound_map.json'
            audio_root = Path(tmpdir) / 'audio'
            map_path.write_text(json.dumps(document))

            with patch('queue_app.sounds.generate.get_default_provider') as get_provider:
                provider = get_provider.return_value
                written = generate_fragments(map_path=map_path, audio_root=audio_root)

            self.assertEqual(len(written), 2)
            self.assertEqual(provider.synthesize.call_count, 2)
            provider.synthesize.assert_any_call(
                text='Nomor antrean',
                output_path=audio_root / 'id/phrases_nomor_antrean.wav',
                lang_code='id',
            )
            provider.synthesize.assert_any_call(
                text='Queue number',
                output_path=audio_root / 'en/phrases_queue_number.wav',
                lang_code='en',
            )

    def test_skips_existing_fragments(self):
        document = {
            'languages': {
                'id': {
                    'lang_code': 'id',
                    'phrases': {
                        'queue_number': {
                            'text': 'Nomor antrean',
                            'file': 'id/phrases_nomor_antrean.wav',
                        },
                        'please_go_to': {
                            'text': 'silakan menuju',
                            'file': 'id/phrases_silakan_menuju.wav',
                        },
                    },
                    'letters': {},
                    'numbers': {},
                    'destinations': {},
                },
            },
        }

        with TemporaryDirectory() as tmpdir:
            map_path = Path(tmpdir) / 'sound_map.json'
            audio_root = Path(tmpdir) / 'audio'
            map_path.write_text(json.dumps(document))
            existing = audio_root / 'id/phrases_nomor_antrean.wav'
            existing.parent.mkdir(parents=True)
            existing.write_bytes(b'RIFF')

            with patch('queue_app.sounds.generate.get_default_provider') as get_provider:
                provider = get_provider.return_value
                written = generate_fragments(map_path=map_path, audio_root=audio_root)

            self.assertEqual(len(written), 1)
            self.assertEqual(provider.synthesize.call_count, 1)
            provider.synthesize.assert_called_once_with(
                text='silakan menuju',
                output_path=audio_root / 'id/phrases_silakan_menuju.wav',
                lang_code='id',
            )
