from rest_framework import serializers
from queue_app.models import Queue, Service

class SingleServiceSerializer(serializers.ModelSerializer):
	class Meta:
		model= Service
		fields = ('id','name', 'desc')

class QueueSerializer(serializers.ModelSerializer):
	service = SingleServiceSerializer(required=False)
	class Meta:
		model= Queue
		fields = ('id', 'number', 'date_created','call_flag', 'service')
		read_only_fields = ('id','number','date_created')