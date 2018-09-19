from django.db import models
from datetime import date

# Create your models here.

class ServiceQueryset(models.QuerySet):
	"""docstring for ServiceQueryset."""
	def get_last_queue(self):
		pass

class Service(models.Model):
	name=models.CharField(max_length = 200)
	desc=models.CharField(max_length = 200)
	date_created=models.DateTimeField(auto_now_add=True)
	date_modified=models.DateTimeField(auto_now=True)
	def __str__(self):
		return self.name

class QueueQueryset(models.QuerySet):
	def get_last_queue(self):
		return self.last()
	def get_today_list(self):
		return self.filter(date_created__date=date.today())

class Queue(models.Model):
	service=models.ForeignKey(
		Service, 
		on_delete=models.CASCADE,
		related_name='queues')
	number=models.IntegerField()
	date_created=models.DateTimeField(auto_now_add=True)
	date_modified=models.DateTimeField(auto_now=True)
	call_flag=models.BooleanField(default=False)
	objects=QueueQueryset.as_manager()
	def __str__(self):
		return self.service.name+'_'+str(self.number)+'_'+str(self.pk)
	class Meta:
		ordering=['date_created']
