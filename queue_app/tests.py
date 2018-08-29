from django.test import TestCase
from queue_app import models
from queue_app import serializers

service = models.Service.objects.get(pk=1)
que = models.Queue.objects.create(service=service,number = 55)
serl = serializers.QueueSerializer(que)
# Create your tests here.
