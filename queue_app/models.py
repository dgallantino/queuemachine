from django.db import models
from datetime import date
from django.contrib.auth.models import AbstractUser
import uuid
	

class Organization(models.Model):
	id=models.UUIDField(
		primary_key=True,
		default=uuid.uuid4,
		editable=False,
	)
	
	name=models.CharField(max_length = 200)
	
	desc=models.CharField(max_length = 200)
	
	date_created=models.DateTimeField(auto_now_add=True)
	
	date_modified=models.DateTimeField(auto_now=True)
	
	
	def __str__(self):
		return self.name
	
class CounterBooth(models.Model):
	
	id=models.UUIDField(
		primary_key=True,
		default=uuid.uuid4,
		editable=False,
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
	
class Role(models.Model):
	
	id=models.UUIDField(
		primary_key=True,
		default=uuid.uuid4,
		editable=False,
	)
	
	name=models.CharField(max_length = 200)
	
	desc=models.CharField(max_length = 200)
	
	date_created=models.DateTimeField(auto_now_add=True)
	
	date_modified=models.DateTimeField(auto_now=True)
	
	def __str__(self):
		return self.name
	
class User(AbstractUser):
	id=models.UUIDField(
		primary_key=True,
		default=uuid.uuid4,
		editable=False)
	
	organization=models.ForeignKey(
		Organization,
		on_delete=models.CASCADE,
		related_name='users',
		null=True,
		blank=True,
	)
	
	def __str__(self):
		return self.username

class ServiceQueryset(models.QuerySet):
	"""docstring for ServiceQueryset."""
	def get_last_queue(self):
		return self.queues.last()

class Service(models.Model):
	
	id=models.UUIDField(
		primary_key=True, 
		default=uuid.uuid4, 
		editable=False)
	
	name=models.CharField(max_length = 200)
	
	desc=models.CharField(max_length = 200)
	
	date_created=models.DateTimeField(auto_now_add=True)
	
	date_modified=models.DateTimeField(auto_now=True)
	
	def __str__(self):
		return self.name

class QueueQueryset(models.QuerySet):
	def get_today_list(self):
		return self.filter(date_created__date=date.today())
	
	def get_nonbooking(self):
		return self.get_today_list().filter(booking_flag=False)
	
	def get_booking(self):
		return self.get_today_list().filter(booking_flag=True)

class Queue(models.Model):
	service=models.ForeignKey(
		Service,
		on_delete=models.CASCADE,
		related_name='queues'
	)
	
	counter_booth=models.ForeignKey(
		CounterBooth,
		on_delete=models.SET_NULL,
		null=True,
		blank=True,
		related_name='queues'
	)
	
	customer=models.ForeignKey(
		User,
		on_delete=models.CASCADE,
		null=True,
		blank=True,
		related_name='queues'
	)
	
	id=models.UUIDField(
		primary_key=True,
		default=uuid.uuid4, 
		editable=False
	)
	
	number=models.IntegerField(
		null=True,
		blank=True
	)
	
	date_created=models.DateTimeField(auto_now_add=True)
	
	date_modified=models.DateTimeField(auto_now=True)
	
	booking_flag=models.BooleanField(default=False)
	
	booking_datetime=models.DateTimeField(null=True,blank=True,)
	
	call_flag=models.BooleanField(default=False)
	
	print_flag=models.BooleanField(default=False)
	
	objects=QueueQueryset.as_manager()
	
	def __str__(self):
		return self.service.name+'/'+str(self.number)+'/'+str(self.pk)
	
	class Meta:
		ordering=['date_created']
		
