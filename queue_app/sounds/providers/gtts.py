"""Google Translate TTS provider for sound fragment generation."""

import logging
import shutil
import subprocess
import tempfile
from io import BytesIO
from pathlib import Path

import requests
from gtts import gTTS
from gtts.tts import gTTSError

from queue_app.sounds.providers.base import TTSProvider
from queue_app.sounds.providers.retry import retry_with_backoff

logger = logging.getLogger(__name__)


def _mp3_bytes_to_wav(mp3_bytes: bytes, wav_path: Path) -> None:
    """Decode MP3 bytes and write a mono WAV file at ``wav_path``."""
    ffmpeg = shutil.which('ffmpeg')
    if ffmpeg is None:
        raise RuntimeError(
            'ffmpeg is required to convert gTTS MP3 output to WAV fragments. '
            'Install ffmpeg and ensure it is on PATH.'
        )

    wav_path.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as mp3_file:
        mp3_file.write(mp3_bytes)
        mp3_path = Path(mp3_file.name)

    try:
        result = subprocess.run(
            [
                ffmpeg,
                '-y',
                '-loglevel',
                'error',
                '-i',
                str(mp3_path),
                '-ar',
                '22050',
                '-ac',
                '1',
                str(wav_path),
            ],
            capture_output=True,
            text=True,
            check=False,
        )
    finally:
        mp3_path.unlink(missing_ok=True)

    if result.returncode != 0:
        detail = (result.stderr or result.stdout or '').strip()
        raise RuntimeError(f'ffmpeg failed to convert MP3 to WAV: {detail}')


class GTTSProvider(TTSProvider):
    """Generate fragments via gTTS with exponential backoff on transient failures."""

    def __init__(
        self,
        *,
        max_attempts: int = 5,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        slow: bool = False,
        timeout: float | tuple[float, float] | None = None,
        lang_check: bool = False,
    ) -> None:
        self.max_attempts = max_attempts
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.slow = slow
        self.timeout = timeout
        self.lang_check = lang_check

    def synthesize(self, text: str, output_path: Path, lang_code: str) -> Path:
        mp3_bytes = retry_with_backoff(
            lambda: self._fetch_mp3(text, lang_code),
            max_attempts=self.max_attempts,
            base_delay=self.base_delay,
            max_delay=self.max_delay,
            retryable_exceptions=(gTTSError, requests.RequestException),
        )
        _mp3_bytes_to_wav(mp3_bytes, output_path)
        logger.debug('Wrote fragment %s', output_path)
        return output_path

    def _fetch_mp3(self, text: str, lang_code: str) -> bytes:
        buf = BytesIO()
        tts = gTTS(
            text=text,
            lang=lang_code,
            slow=self.slow,
            lang_check=self.lang_check,
            timeout=self.timeout,
        )
        tts.write_to_fp(buf)
        return buf.getvalue()
