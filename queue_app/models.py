from django.db import models
from django.utils import timezone

# Create your models here.

class ServiceQueryset(models.QuerySet):
	"""docstring for ServiceQueryset."""
	def add_queue(self, arg):
		pass

class Service(models.Model):
	name=models.CharField(max_length = 200)
	desc=models.CharField(max_length = 200)
	def __str__(self):
		return self.name

class QueueQueryset(models.QuerySet):
	def get_last_queue(self):
		return self.order_by('-id')[0]
	def get_last_service_queue(self, p_service):
		return self.filter(service=p_service)[0]
	def get_new_queues(self, p_last_queue):
		pass

class Queue(models.Model):
	service=models.ForeignKey(Service, on_delete=models.CASCADE)
	number=models.IntegerField()
	date_created=models.DateTimeField(auto_now_add=True)
	date_modified=models.DateTimeField(auto_now=True)
	call_flag=models.BooleanField(default=False)
	objects=QueueQueryset.as_manager()
	class Meta:
		ordering=['-date_created']
