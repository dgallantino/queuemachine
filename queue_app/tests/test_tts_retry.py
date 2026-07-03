"""Tests for TTS provider retry/backoff."""

from unittest import TestCase
from unittest.mock import patch

from queue_app.sounds.providers.retry import retry_with_backoff


class RetryWithBackoffTests(TestCase):
    def test_succeeds_on_first_attempt(self):
        calls = {'count': 0}

        def fn():
            calls['count'] += 1
            return 'ok'

        self.assertEqual(
            retry_with_backoff(fn, max_attempts=3, base_delay=0.01),
            'ok',
        )
        self.assertEqual(calls['count'], 1)

    def test_retries_then_succeeds(self):
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

        self.assertEqual(result, 'done')
        self.assertEqual(calls['count'], 3)
        self.assertEqual(sleep.call_count, 2)

    def test_raises_after_max_attempts(self):
        class TransientError(Exception):
            pass

        def fn():
            raise TransientError('still failing')

        with patch('queue_app.sounds.providers.retry.time.sleep'):
            with self.assertRaises(TransientError):
                retry_with_backoff(
                    fn,
                    max_attempts=3,
                    base_delay=0.01,
                    retryable_exceptions=(TransientError,),
                )
