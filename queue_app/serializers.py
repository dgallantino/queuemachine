from rest_framework import serializers
from queue_app.models import Queue, Service

class NestedServiceSerializer(serializers.ModelSerializer):
	class Meta:
		model= Service
		fields = ('id','name', 'desc')

class QueueSerializer(serializers.ModelSerializer):
	service = NestedServiceSerializer(required=False)
	class Meta:
		model= Queue
		fields = ('id', 'number', 'date_created','call_flag', 'service')
		read_only_fields = ('id','number','date_created')
		
class NestedQueueSerializer(serializers.ModelSerializer):
	class Meta:
		model= Queue
		fields = ('id', 'number', 'date_created','call_flag', 'service')
		read_only_fields = ('id','number','date_created')

class ServiceSerializer(serializers.ModelSerializer):
	queues = NestedQueueSerializer(
		required=False, 
		many=True
		)
	class Meta:
		model=Service
		fields = ('id', 'name', 'desc', 'queues')
		read_only_fields=('id','queues')