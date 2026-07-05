import uuid

from django.db import transaction, IntegrityError

from queue_app import models


class UserService:
    @staticmethod
    @transaction.atomic
    def save_customer(customer, *, save_m2m=None):
        base_username = customer.username
        for attempt in range(5):
            if attempt:
                customer.username = f'{base_username}{uuid.uuid4().hex[:8]}'
            try:
                customer.save()
                break
            except IntegrityError:
                if attempt == 4:
                    raise
        if save_m2m is not None:
            save_m2m()
        return customer
