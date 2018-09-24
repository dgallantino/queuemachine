from rest_framework import serializers, exceptions, status
from django.utils.encoding import force_text
from queue_app.models import Queue, Service

class CustomException(exceptions.APIException):
	status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
	default_detail = 'A server error occurred.'

	def __init__(self, detail, field, status_code):
		if status_code is not None:self.status_code = status_code
		if detail is not None:
			self.detail = {field: force_text(detail)}
		else: self.detail = {'detail': force_text(self.default_detail)}

class NestedServiceSerializer(serializers.ModelSerializer):
	class Meta:
		model= Service
		fields = ('id','name', 'desc')
	def create(self, validated_data):
		return Service.objects.get(pk=2)

class QueueSerializer(serializers.ModelSerializer):
	service = NestedServiceSerializer(
		required=False,
		read_only=True
		)
	class Meta:
		model= Queue
		fields = ('id', 'number', 'call_flag', 'date_created', 'date_modified','service')
		read_only_fields = ('id', 'service','date_created', 'date_modified')
	#deal with this
	def create(self, validated_data):
		try:
			service_data = validated_data.pop('service')
			service_object = Service.objects.get(pk=service_data.get('id'))
			return service_object.queues.create(**validated_data)
		except (KeyError, Service.DoesNotExist):
			raise CustomException('Invalid data', 'service', status_code=status.HTTP_400_BAD_REQUEST)
	def update(self, instance, validated_data):
		if instance.number == validated_data.get('number'):
			instance.call_flag = validated_data.pop('call_flag')
			instance.save()
			return instance
		raise CustomException('Invalid data','number', status_code=status.HTTP_400_BAD_REQUEST)

	
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

		