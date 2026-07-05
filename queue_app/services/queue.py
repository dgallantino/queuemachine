from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from queue_app import models


class QueueService:
    @staticmethod
    def _next_number(service, *, exclude_queue_id=None):
        today = timezone.localdate()
        qs = models.Queue.objects.filter(
            service=service,
            is_printed=True,
            print_datetime__date=today,
        )
        if exclude_queue_id is not None:
            qs = qs.exclude(pk=exclude_queue_id)
        last_number = qs.order_by('-number').values_list('number', flat=True).first()
        return (last_number or 0) + 1

    @staticmethod
    @transaction.atomic
    def assign_ticket_number(queue):
        """Assign queue number and print timestamp under a service lock."""
        if not queue.pk:
            queue.is_printed = False
            queue.save()

        locked_queue = (
            models.Queue.objects
            .select_for_update()
            .select_related('service')
            .get(pk=queue.pk)
        )
        if locked_queue.is_printed and locked_queue.number is not None:
            return locked_queue

        service = models.Service.objects.select_for_update().get(pk=locked_queue.service_id)
        locked_queue.number = QueueService._next_number(service)
        locked_queue.is_printed = True
        locked_queue.print_datetime = locked_queue.print_datetime or timezone.now()
        locked_queue.character = locked_queue.character or service.queue_char
        locked_queue.save()
        return locked_queue

    @staticmethod
    @transaction.atomic
    def call_queue(queue, counter_booth):
        locked_queue = (
            models.Queue.objects
            .select_for_update()
            .select_related('service', 'service__organization')
            .get(pk=queue.pk)
        )
        if not locked_queue.is_printed:
            raise ValidationError(_('queue must be printed before it can be called'))
        if locked_queue.is_finished:
            raise ValidationError(_('queue is already finished'))
        if counter_booth is None:
            raise ValidationError(_('counter booth is required'))
        if counter_booth.organization_id != locked_queue.service.organization_id:
            raise ValidationError(_('counter booth does not belong to this organization'))

        locked_queue.is_called = True
        locked_queue.counter_booth = counter_booth
        locked_queue.save()
        return locked_queue

    @staticmethod
    @transaction.atomic
    def finish_queue(queue):
        locked_queue = models.Queue.objects.select_for_update().get(pk=queue.pk)
        locked_queue.is_finished = True
        locked_queue.save()
        return locked_queue

    @staticmethod
    @transaction.atomic
    def move_queue(queue, target_service):
        locked_queue = (
            models.Queue.objects
            .select_for_update()
            .select_related('service')
            .get(pk=queue.pk)
        )
        target_service = models.Service.objects.select_for_update().get(pk=target_service.pk)

        if target_service.organization_id != locked_queue.service.organization_id:
            raise ValidationError(_('target service does not belong to this organization'))
        if locked_queue.service_id == target_service.id:
            return locked_queue
        if not locked_queue.is_printed:
            raise ValidationError(_('queue must be printed before it can be moved'))

        locked_queue.service = target_service
        locked_queue.is_called = False
        locked_queue.is_finished = False
        locked_queue.counter_booth = None
        locked_queue.number = QueueService._next_number(
            target_service,
            exclude_queue_id=locked_queue.pk,
        )
        locked_queue.print_datetime = timezone.now()
        locked_queue.character = target_service.queue_char
        locked_queue.save()
        return locked_queue
