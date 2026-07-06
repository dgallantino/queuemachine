from concurrent.futures import ThreadPoolExecutor, as_completed

import pytest
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import connections

from queue_app.models import CounterBooth, Organization, Queue, Service
from queue_app.services import QueueService


@pytest.fixture
def queue_service_setup(db):
    organization = Organization.objects.create(name='Test Org')
    other_organization = Organization.objects.create(name='Other Org')
    service = Service.objects.create(
        organization=organization,
        name='General',
        queue_char='A',
    )
    other_service = Service.objects.create(
        organization=organization,
        name='Billing',
        queue_char='B',
    )
    foreign_service = Service.objects.create(
        organization=other_organization,
        name='Foreign',
        queue_char='C',
    )
    booth = CounterBooth.objects.create(
        organization=organization,
        display_name='Booth 1',
        spoken_name='booth one',
    )
    foreign_booth = CounterBooth.objects.create(
        organization=other_organization,
        display_name='Foreign Booth',
        spoken_name='foreign booth',
    )
    return {
        'organization': organization,
        'other_organization': other_organization,
        'service': service,
        'other_service': other_service,
        'foreign_service': foreign_service,
        'booth': booth,
        'foreign_booth': foreign_booth,
    }


@pytest.mark.django_db
def test_assign_ticket_number_is_sequential(queue_service_setup):
    service = queue_service_setup['service']
    first = Queue.objects.create(service=service)
    second = Queue.objects.create(service=service)

    QueueService.assign_ticket_number(first)
    QueueService.assign_ticket_number(second)

    first.refresh_from_db()
    second.refresh_from_db()
    assert first.number == 1
    assert second.number == 2
    assert first.is_printed
    assert second.is_printed
    assert first.print_datetime is not None
    assert second.print_datetime is not None


@pytest.mark.django_db
def test_assign_ticket_number_is_idempotent(queue_service_setup):
    service = queue_service_setup['service']
    queue = Queue.objects.create(service=service)
    printed = QueueService.assign_ticket_number(queue)
    again = QueueService.assign_ticket_number(printed)

    again.refresh_from_db()
    assert again.number == printed.number
    assert Queue.objects.filter(service=service, number=1).count() == 1


@pytest.mark.django_db
def test_call_queue_sets_booth_atomically(queue_service_setup):
    service = queue_service_setup['service']
    booth = queue_service_setup['booth']
    queue = Queue.objects.create(service=service)
    QueueService.assign_ticket_number(queue)

    called = QueueService.call_queue(queue, booth)

    called.refresh_from_db()
    assert called.is_called
    assert called.counter_booth_id == booth.id


@pytest.mark.django_db
def test_call_queue_rejects_unprinted_queue(queue_service_setup):
    service = queue_service_setup['service']
    booth = queue_service_setup['booth']
    queue = Queue.objects.create(service=service)
    with pytest.raises(ValidationError):
        QueueService.call_queue(queue, booth)


@pytest.mark.django_db
def test_call_queue_rejects_foreign_booth(queue_service_setup):
    service = queue_service_setup['service']
    foreign_booth = queue_service_setup['foreign_booth']
    queue = Queue.objects.create(service=service)
    QueueService.assign_ticket_number(queue)
    with pytest.raises(ValidationError):
        QueueService.call_queue(queue, foreign_booth)


@pytest.mark.django_db
def test_move_queue_renumbers_in_target_service(queue_service_setup):
    service = queue_service_setup['service']
    other_service = queue_service_setup['other_service']
    source_queue = Queue.objects.create(service=service)
    QueueService.assign_ticket_number(source_queue)
    existing_target = Queue.objects.create(service=other_service)
    QueueService.assign_ticket_number(existing_target)

    moved = QueueService.move_queue(source_queue, other_service)

    moved.refresh_from_db()
    assert moved.service_id == other_service.id
    assert moved.number == 2
    assert not moved.is_called
    assert moved.counter_booth_id is None
    assert not moved.is_finished
    assert moved.character == 'B'


@pytest.mark.django_db
def test_move_queue_rejects_foreign_service(queue_service_setup):
    service = queue_service_setup['service']
    foreign_service = queue_service_setup['foreign_service']
    queue = Queue.objects.create(service=service)
    QueueService.assign_ticket_number(queue)
    with pytest.raises(ValidationError):
        QueueService.move_queue(queue, foreign_service)


@pytest.mark.django_db
def test_finish_queue_marks_finished(queue_service_setup):
    service = queue_service_setup['service']
    queue = Queue.objects.create(service=service)
    QueueService.assign_ticket_number(queue)

    finished = QueueService.finish_queue(queue)

    finished.refresh_from_db()
    assert finished.is_finished


@pytest.fixture
def concurrent_queue_setup(db):
    organization = Organization.objects.create(name='Concurrent Org')
    service = Service.objects.create(
        organization=organization,
        name='General',
        queue_char='A',
    )
    return {'organization': organization, 'service': service}


@pytest.mark.skipif(
    settings.DATABASES['default']['ENGINE'] == 'django.db.backends.sqlite3',
    reason='SQLite does not support concurrent writes from multiple threads',
)
@pytest.mark.django_db(transaction=True)
def test_concurrent_assignments_produce_unique_numbers(concurrent_queue_setup):
    service = concurrent_queue_setup['service']
    queues = [Queue.objects.create(service=service) for _ in range(8)]
    numbers = []

    def assign(queue):
        connections.close_all()
        printed = QueueService.assign_ticket_number(queue)
        return printed.number

    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = [executor.submit(assign, queue) for queue in queues]
        for future in as_completed(futures):
            numbers.append(future.result())

    assert len(numbers) == len(set(numbers))
    assert sorted(numbers) == list(range(1, 9))


@pytest.mark.skipif(
    settings.DATABASES['default']['ENGINE'] == 'django.db.backends.sqlite3',
    reason='SQLite does not support concurrent writes from multiple threads',
)
@pytest.mark.django_db(transaction=True)
def test_concurrent_moves_produce_unique_target_numbers(concurrent_queue_setup):
    organization = concurrent_queue_setup['organization']
    service = concurrent_queue_setup['service']
    target = Service.objects.create(
        organization=organization,
        name='Target',
        queue_char='B',
    )
    seed = Queue.objects.create(service=target)
    QueueService.assign_ticket_number(seed)

    queues = [Queue.objects.create(service=service) for _ in range(5)]
    for queue in queues:
        QueueService.assign_ticket_number(queue)

    moved_numbers = []

    def move(queue):
        connections.close_all()
        moved = QueueService.move_queue(queue, target)
        return moved.number

    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(move, queue) for queue in queues]
        for future in as_completed(futures):
            moved_numbers.append(future.result())

    assert len(moved_numbers) == len(set(moved_numbers))
    assert sorted(moved_numbers) == list(range(2, 7))
