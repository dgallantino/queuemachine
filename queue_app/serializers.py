from rest_framework import serializers
from queue_app.models import Queue, Service

class NestedServiceSerializer(serializers.ModelSerializer):
	class Meta:
		model= Service
		fields = ('id','name', 'desc')

class QueueSerializer(serializers.ModelSerializer):
	service = NestedServiceSerializer(required=True)
	class Meta:
		model= Queue
		fields = ('id', 'number', 'call_flag', 'date_created', 'date_modified','service')
		read_only_fields = ('id','date_created', 'date_modified')
	def create(self, validated_data):
		#KeyError Exception
		service_data = validated_data.pop('service')
		#Service.DoesNotExsist Exception
		service_object = Service.objects.get(pk=service_data.get('id'))
		return service_object.queues.create(**validated_data)
	def update(self, instance, validated_data):
		call_flag = validated_data.pop('call_flag')
		instance.call_flag = call_flag
		instance.save()
		return instance
	
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