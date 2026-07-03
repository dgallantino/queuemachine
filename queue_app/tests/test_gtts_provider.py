"""Tests for the gTTS sound fragment provider."""

from io import BytesIO
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import MagicMock, patch

from gtts.tts import gTTSError

from queue_app.sounds.providers.gtts import GTTSProvider


class GTTSProviderTests(TestCase):
    def test_synthesize_retries_then_writes_wav(self):
        provider = GTTSProvider(max_attempts=3, base_delay=0.01)
        attempts = {'count': 0}

        def fake_fetch(text, lang_code):
            attempts['count'] += 1
            if attempts['count'] < 2:
                raise gTTSError('503 from TTS API')
            return b'fake-mp3-bytes'

        with TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / 'fragment.wav'

            with patch.object(provider, '_fetch_mp3', side_effect=fake_fetch):
                with patch(
                    'queue_app.sounds.providers.gtts._mp3_bytes_to_wav',
                ) as convert:
                    result = provider.synthesize('hello', output_path, 'id')

            self.assertEqual(result, output_path)
            self.assertEqual(attempts['count'], 2)
            convert.assert_called_once_with(b'fake-mp3-bytes', output_path)

    def test_fetch_mp3_uses_gtts(self):
        provider = GTTSProvider()
        fake_tts = MagicMock()

        with patch('queue_app.sounds.providers.gtts.gTTS', return_value=fake_tts) as gtts_cls:
            result = provider._fetch_mp3('nomor antrean', 'id')

        gtts_cls.assert_called_once_with(
            text='nomor antrean',
            lang='id',
            slow=False,
            lang_check=False,
            timeout=None,
        )
        fake_tts.write_to_fp.assert_called_once()
        self.assertIsInstance(fake_tts.write_to_fp.call_args[0][0], BytesIO)
        self.assertEqual(result, fake_tts.write_to_fp.call_args[0][0].getvalue())
