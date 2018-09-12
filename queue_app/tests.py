from django.test import TestCase


from queue_app.models import Queue, Service
from queue_app.serializers import QueueSerializer, NestedServiceSerializer
service = Service.objects.get(pk=1)
que = Queue.objects.create(service=service,number = 55)
serl = QueueSerializer(que)
queue_data = {'number':9999,'call_flag':False,'service':{'id':55, 'name':'utoeunt','desc':'aoeuao'}}

# Create your tests here.
