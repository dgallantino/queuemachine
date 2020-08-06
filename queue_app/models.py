from django.db import models
from django.utils.translation import gettext_lazy as _
from datetime import date
from django.contrib.auth.models import AbstractUser, Group
import uuid


class Organization(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    date_created = models.DateTimeField(auto_now_add=True)

    date_modified = models.DateTimeField(auto_now=True)

    name = models.CharField(
        max_length=20,
        verbose_name=_('name'),
    )

    def __str__(self):
        return self.name

    def to_flat_dict(self):
        return {
            'id': str(self.id),
            'name': self.name,
        }

    class Meta:
        verbose_name = _('organization')
        verbose_name_plural = verbose_name


class CounterBooth(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    groups = models.ForeignKey(
        Group,
        blank=True,
        related_name='booths',
        on_delete=models.CASCADE,
        null=True,
        verbose_name=_('groups'),
    )

    display_name = models.CharField(
        max_length=20,
        verbose_name=_('display name'),
    )

    spoken_name = models.CharField(
        max_length=30,
        verbose_name=_('spoken name'),
    )

    desc = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        verbose_name=_('description'),
    )

    date_created = models.DateTimeField(auto_now_add=True)

    date_modified = models.DateTimeField(auto_now=True)

    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='counter_booth',
        null=False,
        blank=False,
        verbose_name=_('organization'),
    )

    def __str__(self):
        return self.display_name

    def to_flat_dict(self):
        return {
            'id': str(self.id),
            'display_name': self.display_name,
            'spoken_name': self.spoken_name,
            'desc': self.desc,
            'organization': str(self.organization.id or 'null'),
            # 'group': str(self.groups.id or 'null'),
        }

    def latest_queue(self):
        return self.queues.today_filter().order_by('date_modified').last()

    class Meta:
        verbose_name = _('counter booth')
        verbose_name_plural = verbose_name


class User(AbstractUser):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    organization = models.ManyToManyField(
        Organization,
        related_name='users',
        blank=False,
        verbose_name=_('organization')
    )

    phone = models.CharField(
        null=True,
        blank=True,
        max_length=12,
        verbose_name=_('phone number')
    )

    def __str__(self):
        return self.username


# class CustomerProfile(models.Model):
# 	id=models.UUIDField(
# 		primary_key=True,
# 		default=uuid.uuid4,
# 		editable=False
# 	)
#
# 	user=models.OneToOneField(
# 		User,
# 		on_delete=models.CASCADE,
# 		related_name='customer_profile'
# 	)
#
# 	groups=models.ManyToManyField(
# 		Group,
# 		blank=True,
# 		related_name='customers',
# 	)
#
# 	birth_modified=models.DateTimeField(null=True,blank=True)
#
# 	first_name = models.CharField(max_length=20)
#
# 	last_name = models.CharField(max_length=20)
#
# 	email = models.EmailField()
#
# 	address = models.CharField(max_length=200)
#
# 	phone=models.CharField(
# 		null=True,
# 		blank=True,
# 		max_length = 12,
# 	)
#
# 	date_created=models.DateTimeField(auto_now_add=True)
#
# 	date_modified=models.DateTimeField(auto_now=True)

class ServiceQueryset(models.QuerySet):
    """docstring for ServiceQueryset."""

    def get_last_queue(self):
        return self.queues.last()

    def groups_filter(self, iterable):
        return self.filter(group__in=iterable)

    def group_filter(self, group_obj):
        return self.filter(group=group_obj)

    def org_filter(self, org):
        return self.filter(organization=org)

    def orgs_filter(self, orgs):
        return self.filter(organization__in=orgs)

    def is_hidden(self, flag=None):
        if flag is not None:
            return self.filter(is_hidden=flag)
        return self


class Service(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    date_created = models.DateTimeField(auto_now_add=True)

    date_modified = models.DateTimeField(auto_now=True)

    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='services',
        null=False,
        # null=True,
        blank=False,
        verbose_name=_('organization'),
    )

    group = models.ForeignKey(
        Group,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='services',
        verbose_name=_('group'),
    )

    name = models.CharField(
        max_length=30,
        verbose_name=_('name'),
    )

    desc = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        verbose_name=_('description'),
    )

    queue_char = models.CharField(
        null=True,
        blank=True,
        max_length=1,
        verbose_name=_('queue character'),
    )

    is_hidden = models.BooleanField(default=False, verbose_name=_('hide'))

    objects = ServiceQueryset.as_manager()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('service')
        verbose_name_plural = verbose_name


class QueueQueryset(models.QuerySet):
    def today_filter(self):
        return self.filter(date_created__date=date.today())

    def is_printed(self, flag=None):
        if flag is not None:
            return self.filter(is_printed=flag)
        return self

    def is_booking(self, flag=None):
        if flag is not None:
            return self.filter(is_booking=flag)
        return self

    def is_called(self, flag=None):
        if flag is not None:
            return self.filter(is_called=flag)
        return self

    def is_finished(self, flag=None):
        if flag is not None:
            return self.filter(is_finished=flag)
        return self

    def services_filter(self, iterable):
        return self.filter(service__in=iterable)

    def last_modified(self):
        return self.order_by('date_modified').last()


class Queue(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    date_created = models.DateTimeField(auto_now_add=True, verbose_name=_('date created'))

    date_modified = models.DateTimeField(auto_now=True, verbose_name=_('date modified'))

    service = models.ForeignKey(
        Service,
        on_delete=models.CASCADE,
        related_name='queues',
        null=False,
        blank=False,
        verbose_name=_('service'),
    )  #

    character = models.CharField(
        null=True,
        blank=True,
        max_length=1,
        verbose_name=_('character'),

    )

    # calculated by forms
    number = models.IntegerField(
        null=True,
        blank=True,
        verbose_name=_('number'),
    )

    customer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='queues',
        verbose_name=_('customer'),

    )  #

    counter_booth = models.ForeignKey(
        CounterBooth,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='queues',
        verbose_name=_('counter'),

    )  #

    is_booking = models.BooleanField(default=False, verbose_name=_('booking'))  #

    is_called = models.BooleanField(default=False, verbose_name=_('called'))  #

    is_printed = models.BooleanField(default=False, verbose_name=_('printed'))  #

    is_finished = models.BooleanField(default=False, verbose_name=_('finished'))  #

    booking_datetime = models.DateTimeField(null=True, blank=True, verbose_name=_('booking date time'))

    print_datetime = models.DateTimeField(null=True, blank=True, verbose_name=_('print date time'))

    objects = QueueQueryset.as_manager()

    def __str__(self):
        return self.service.name + '/' + str(self.number) + '/' + str(self.pk)

    def save(self, *args, **kwargs):
        self.character = self.character or self.service.queue_char
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['date_created']
        verbose_name = _('queue')
        verbose_name_plural = verbose_name
