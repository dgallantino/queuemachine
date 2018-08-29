from rest_framework import serializers
from queue_app.models import Queue

class QueueSerializer(serializers.ModelSerializer):
	# def create(self, validated_data):
	# 	print(validated_data)
	# 	return Queue.objects.create(**validated_data)
	# def update(self, instance, validated_data):
	# 	instance.call_flag = validated_data.get()
	service_name = serializers.RelatedField(read_only=True, many=True)
	class Meta:
		model= Queue
		fields = ('id','service', 'service_name', 'number', 'date_created','date_modified','call_flag')
		read_only_fields = ('id','number','created','service', 'service_name', 'date_modified')
