from django.db import models
from datetime import date
from django.contrib.auth.models import AbstractUser, Group
import uuid
	
#todos:
#separate employee and costomer : using staf flag

# Organization will be deprocated
# Using Group instead
class Organization(models.Model):
	id=models.UUIDField(
		primary_key=True,
		default=uuid.uuid4,
		editable=False,
	)
	date_created=models.DateTimeField(auto_now_add=True)
	
	date_modified=models.DateTimeField(auto_now=True)
	
	name=models.CharField(max_length = 200)
	
	desc=models.CharField(max_length = 200)
	
	
	def __str__(self):
		return self.name
	
class CounterBooth(models.Model):
	
	id=models.UUIDField(
		primary_key=True,
		default=uuid.uuid4,
		editable=False,
	)
	
	groups=models.ManyToManyField(
		Group,
		blank=True,
		related_name='booths',
	)
	
	name=models.CharField(max_length = 200)
	
	desc=models.CharField(max_length = 200)
	
	date_created=models.DateTimeField(auto_now_add=True)
	
	date_modified=models.DateTimeField(auto_now=True)
	
	organization=models.ForeignKey(
		Organization,
		on_delete=models.CASCADE,
		related_name='counter_booth',
		null=True,
		blank=False,
	)
	
	def __str__(self):
		return self.name
	
class User(AbstractUser):
	id=models.UUIDField(
		primary_key=True,
		default=uuid.uuid4,
		editable=False
	)
	
	organization=models.ForeignKey(
		Organization,
		on_delete=models.CASCADE,
		related_name='users',
		null=True,
		blank=True,
	)
	
	phone=models.CharField(
		null=True,
		blank=True,
		max_length = 12,
	)
	
	def __str__(self):
		return self.username

class ServiceQueryset(models.QuerySet):
	"""docstring for ServiceQueryset."""
	def get_last_queue(self):
		return self.queues.last()
	def group_filter(self, iterable):
		return self.filter(groups__in=iterable)

class Service(models.Model):
	
	id=models.UUIDField(
		primary_key=True, 
		default=uuid.uuid4, 
		editable=False,
	)
	
	date_created=models.DateTimeField(auto_now_add=True)
	
	date_modified=models.DateTimeField(auto_now=True)
	
	organization=models.ForeignKey(
		Organization,
		on_delete=models.CASCADE,
		related_name='services',
		null=True,
		blank=False,
	)
	
	groups=models.ManyToManyField(
		Group,
		blank=True,
		related_name='services',
	)
	
	name=models.CharField(max_length = 200)
	
	desc=models.CharField(max_length = 200)
	
	queue_char=models.CharField(
		null=True,
		blank=True,
		max_length=1,
	)
	
	objects=ServiceQueryset.as_manager()
	
	def __str__(self):
		return self.name


class QueueQueryset(models.QuerySet):
	
	def is_printed(self, flag=False):
		return self.filter(print_flag=flag)
	
	def get_today(self):
		return self.filter(date_created__date=date.today())
	
	def is_booking(self, flag=False):
		return self.get_today().filter(booking_flag=flag)
	
	def services_filter(self, iterable):
		return self.filter(service__in=iterable)

class Queue(models.Model):
	id=models.UUIDField(
		primary_key=True,
		default=uuid.uuid4, 
		editable=False
	)
	
	date_created=models.DateTimeField(auto_now_add=True)
	
	date_modified=models.DateTimeField(auto_now=True)
	
	service=models.ForeignKey(
		Service,
		on_delete=models.CASCADE,
		related_name='queues'
	)#
	
	character=models.CharField(
		null=True,
		blank=True,
		max_length=1,
	)#
	
	number=models.IntegerField(
		null=True,
		blank=True
	)
	
	customer=models.ForeignKey(
		User,
		on_delete=models.CASCADE,
		null=True,
		blank=True,
		related_name='queues'
	)#
	
	counter_booth=models.ForeignKey(
		CounterBooth,
		on_delete=models.SET_NULL,
		null=True,
		blank=True,
		related_name='queues'
	)#
	
	booking_flag=models.BooleanField(default=False)#
		
	call_flag=models.BooleanField(default=False)#
	
	print_flag=models.BooleanField(default=False)#
	
	booking_datetime=models.DateTimeField(null=True,blank=True,)
	
	print_datetime=models.DateTimeField(null=True, blank=True)
	
	objects=QueueQueryset.as_manager()
	
	def __str__(self):
		return self.service.name+'/'+str(self.number)+'/'+str(self.pk)
	
	def save(self, *args, **kwargs):
		self.character = self.character or self.service.queue_char
		super().save(*args, **kwargs)
	
	class Meta:
		ordering=['date_created']
		
