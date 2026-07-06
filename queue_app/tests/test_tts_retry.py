"""Tests for TTS provider retry/backoff."""

from unittest.mock import patch

import pytest

from queue_app.sounds.providers.retry import retry_with_backoff


def test_succeeds_on_first_attempt():
    calls = {'count': 0}

    def fn():
        calls['count'] += 1
        return 'ok'

    assert retry_with_backoff(fn, max_attempts=3, base_delay=0.01) == 'ok'
    assert calls['count'] == 1


def test_retries_then_succeeds():
    calls = {'count': 0}

    class TransientError(Exception):
        pass

    def fn():
        calls['count'] += 1
        if calls['count'] < 3:
            raise TransientError('temporary')
        return 'done'

    with patch('queue_app.sounds.providers.retry.time.sleep') as sleep:
        result = retry_with_backoff(
            fn,
            max_attempts=5,
            base_delay=0.01,
            retryable_exceptions=(TransientError,),
        )

    assert result == 'done'
    assert calls['count'] == 3
    assert sleep.call_count == 2


def test_raises_after_max_attempts():
    class TransientError(Exception):
        pass

    def fn():
        raise TransientError('still failing')

    with patch('queue_app.sounds.providers.retry.time.sleep'):
        with pytest.raises(TransientError):
            retry_with_backoff(
                fn,
                max_attempts=3,
                base_delay=0.01,
                retryable_exceptions=(TransientError,),
            )
