"""TTS provider interfaces for sound fragment generation."""

from abc import ABC, abstractmethod
from pathlib import Path


class TTSProvider(ABC):
    """Abstract text-to-speech backend (gTTS, cloud APIs, local models, etc.)."""

    @abstractmethod
    def synthesize(self, text: str, output_path: Path, lang_code: str) -> Path:
        """Synthesize ``text`` and write audio to ``output_path``."""


class StubTTSProvider(TTSProvider):
    """Placeholder provider used until a real backend is wired in."""

    def synthesize(self, text: str, output_path: Path, lang_code: str) -> Path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.touch()
        return output_path


def get_default_provider() -> TTSProvider:
    """Return the active TTS provider."""
    from queue_app.sounds.providers.gtts import GTTSProvider

    return GTTSProvider()
