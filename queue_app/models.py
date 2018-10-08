from django.db import models
from datetime import date
import uuid
from django.contrib.auth.models import User

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
	
class CounterBooth(models.Model): 
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

class Queue(models.Model):
	service=models.ForeignKey(
		Service, 
		on_delete=models.CASCADE,
		related_name='queues')
	counter_booth=models.ForeignKey(
		CounterBooth,
		on_delete=models.SET_NULL,
		null=True,
		blank=True,
		related_name='queues')
	customer=models.ForeignKey(
		User,
		on_delete=models.CASCADE,
		null=True,
		blank=True,
		related_name='queues')
	id=models.UUIDField(
		primary_key=True,
		default=uuid.uuid4, 
		editable=False)
	number=models.IntegerField(
		null=True,
		blank=True)
	date_created=models.DateTimeField(auto_now_add=True)
	date_modified=models.DateTimeField(auto_now=True)
	booking_flag=models.BooleanField(default=False)
	booking_time=models.DateTimeField(null=True,blank=True,)
	call_flag=models.BooleanField(default=False)
	objects=QueueQueryset.as_manager()
	def __str__(self):
		return self.service.name+'/'+str(self.number)+'/'+str(self.pk)
	class Meta:
		ordering=['date_created']
