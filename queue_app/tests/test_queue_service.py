from concurrent.futures import ThreadPoolExecutor, as_completed

from django.core.exceptions import ValidationError
from django.test import TestCase, TransactionTestCase

from queue_app.models import CounterBooth, Organization, Queue, Service, User
from queue_app.services import QueueService


class QueueServiceTestCase(TestCase):
    def setUp(self):
        self.organization = Organization.objects.create(name='Test Org')
        self.other_organization = Organization.objects.create(name='Other Org')
        self.service = Service.objects.create(
            organization=self.organization,
            name='General',
            queue_char='A',
        )
        self.other_service = Service.objects.create(
            organization=self.organization,
            name='Billing',
            queue_char='B',
        )
        self.foreign_service = Service.objects.create(
            organization=self.other_organization,
            name='Foreign',
            queue_char='C',
        )
        self.booth = CounterBooth.objects.create(
            organization=self.organization,
            display_name='Booth 1',
            spoken_name='booth one',
        )
        self.foreign_booth = CounterBooth.objects.create(
            organization=self.other_organization,
            display_name='Foreign Booth',
            spoken_name='foreign booth',
        )

    def test_assign_ticket_number_is_sequential(self):
        first = Queue.objects.create(service=self.service)
        second = Queue.objects.create(service=self.service)

        QueueService.assign_ticket_number(first)
        QueueService.assign_ticket_number(second)

        first.refresh_from_db()
        second.refresh_from_db()
        self.assertEqual(first.number, 1)
        self.assertEqual(second.number, 2)
        self.assertTrue(first.is_printed)
        self.assertTrue(second.is_printed)
        self.assertIsNotNone(first.print_datetime)
        self.assertIsNotNone(second.print_datetime)

    def test_assign_ticket_number_is_idempotent(self):
        queue = Queue.objects.create(service=self.service)
        printed = QueueService.assign_ticket_number(queue)
        again = QueueService.assign_ticket_number(printed)

        again.refresh_from_db()
        self.assertEqual(again.number, printed.number)
        self.assertEqual(Queue.objects.filter(service=self.service, number=1).count(), 1)

    def test_call_queue_sets_booth_atomically(self):
        queue = Queue.objects.create(service=self.service)
        QueueService.assign_ticket_number(queue)

        called = QueueService.call_queue(queue, self.booth)

        called.refresh_from_db()
        self.assertTrue(called.is_called)
        self.assertEqual(called.counter_booth_id, self.booth.id)

    def test_call_queue_rejects_unprinted_queue(self):
        queue = Queue.objects.create(service=self.service)
        with self.assertRaises(ValidationError):
            QueueService.call_queue(queue, self.booth)

    def test_call_queue_rejects_foreign_booth(self):
        queue = Queue.objects.create(service=self.service)
        QueueService.assign_ticket_number(queue)
        with self.assertRaises(ValidationError):
            QueueService.call_queue(queue, self.foreign_booth)

    def test_move_queue_renumbers_in_target_service(self):
        source_queue = Queue.objects.create(service=self.service)
        QueueService.assign_ticket_number(source_queue)
        existing_target = Queue.objects.create(service=self.other_service)
        QueueService.assign_ticket_number(existing_target)

        moved = QueueService.move_queue(source_queue, self.other_service)

        moved.refresh_from_db()
        self.assertEqual(moved.service_id, self.other_service.id)
        self.assertEqual(moved.number, 2)
        self.assertFalse(moved.is_called)
        self.assertIsNone(moved.counter_booth_id)
        self.assertFalse(moved.is_finished)
        self.assertEqual(moved.character, 'B')

    def test_move_queue_rejects_foreign_service(self):
        queue = Queue.objects.create(service=self.service)
        QueueService.assign_ticket_number(queue)
        with self.assertRaises(ValidationError):
            QueueService.move_queue(queue, self.foreign_service)

    def test_finish_queue_marks_finished(self):
        queue = Queue.objects.create(service=self.service)
        QueueService.assign_ticket_number(queue)

        finished = QueueService.finish_queue(queue)

        finished.refresh_from_db()
        self.assertTrue(finished.is_finished)


class QueueServiceConcurrencyTestCase(TransactionTestCase):
    def setUp(self):
        self.organization = Organization.objects.create(name='Concurrent Org')
        self.service = Service.objects.create(
            organization=self.organization,
            name='General',
            queue_char='A',
        )

    def test_concurrent_assignments_produce_unique_numbers(self):
        queues = [Queue.objects.create(service=self.service) for _ in range(8)]
        numbers = []

        def assign(queue):
            printed = QueueService.assign_ticket_number(queue)
            return printed.number

        with ThreadPoolExecutor(max_workers=8) as executor:
            futures = [executor.submit(assign, queue) for queue in queues]
            for future in as_completed(futures):
                numbers.append(future.result())

        self.assertEqual(len(numbers), len(set(numbers)))
        self.assertEqual(sorted(numbers), list(range(1, 9)))

    def test_concurrent_moves_produce_unique_target_numbers(self):
        target = Service.objects.create(
            organization=self.organization,
            name='Target',
            queue_char='B',
        )
        seed = Queue.objects.create(service=target)
        QueueService.assign_ticket_number(seed)

        queues = [Queue.objects.create(service=self.service) for _ in range(5)]
        for queue in queues:
            QueueService.assign_ticket_number(queue)

        moved_numbers = []

        def move(queue):
            moved = QueueService.move_queue(queue, target)
            return moved.number

        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(move, queue) for queue in queues]
            for future in as_completed(futures):
                moved_numbers.append(future.result())

        self.assertEqual(len(moved_numbers), len(set(moved_numbers)))
        self.assertEqual(sorted(moved_numbers), list(range(2, 7)))
