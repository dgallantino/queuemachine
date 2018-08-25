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
	def last_queue(self):
		return self.order_by('-id')[0]
	def last_queue_by_service(self, service):
		return self.filter(service=service).order_by('-id')[0]

class Queue(models.Model):
	service=models.ForeignKey(Service, on_delete=models.CASCADE)
	number=models.IntegerField()
	created=models.DateTimeField(default=timezone.now)
	objects=QueueQueryset.as_manager()
