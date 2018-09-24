from queue_app.models import Service, Queue
from queue_app import serializers
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, TemplateView
from django.http import JsonResponse

from rest_framework import status, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authentication import SessionAuthentication, BasicAuthentication 
from rest_framework.permissions import IsAdminUser
from rest_framework.exceptions import NotFound, ParseError



class IndexView(TemplateView):
	template_name = 'queue_app/index.html'
	def get(self, request, *args, **kwargs):
		return TemplateView.get(self, request, *args, **kwargs)
	

class MachineDisplay(LoginRequiredMixin, ListView):
	login_url = '/accounts/login/'
	template_name ='queue_app/machine.html'
	model = Service

'''
decomissioned
API implementation without django rest framework
'''
class PrintTicketView(LoginRequiredMixin, DetailView):
	template_name ='queue_app/test.html'
	model = Service
	http_method_names = ['get', 'post']
	object_name = 'queue';
	def add_next_queue(self, service):
		last_queue = service.queues.get_today_list().last()
		if last_queue:
			next_queue = service.queues.create(
				number = last_queue.number + 1
				)
			return next_queue
		next_queue = service.queues.create(number = 1)	
		return next_queue
	def get(self, request, *args, **kwargs):		
		return JsonResponse(serializers.QueueSerializer(self.add_next_queue(self.get_object())).data)
	
class PrintTicketApi(APIView):
	http_method_names=('post')
	authentication_classes = (SessionAuthentication, BasicAuthentication)
	permission_classes = (IsAdminUser,)
	serialier_class = serializers.ServiceSerializer
	def add_next_queue(self, service):
		last_queue = service.queues.last()
		if last_queue:
			next_queue = service.queues.create(
				number = last_queue.number + 1
				)
			return next_queue
		next_queue = service.queues.create(number = 1)	
		return next_queue
	def get_object(self,pk):
		try:
			return Service.objects.get(pk=pk)
		except Service.DoesNotExist:
			raise NotFound(detail="Object not found", code=404)
	def post(self, request):
		if 'pk' in request.data:
			service = self.get_object(request.data.get('pk'))
			if service.name == request.data.get('service') :
				return Response(
					serializers.QueueSerializer(self.add_next_queue(service)).data,
						status=status.HTTP_201_CREATED
					)
		raise ParseError(detail="Bad request", code=400)
	
'''
Manager page Views
'''
class ManagerDisplay(LoginRequiredMixin, ListView):
	template_name='queue_app/manager.html'
	model = Service
	context_object_name = 'Services'
	
'''
API: Update Queue in manager list
using retrive instead of list becouse you need the data of the last listed queue
'''
class QueueRetriveUpdateAPI(generics.RetrieveUpdateAPIView):
	authentication_classes = (SessionAuthentication, BasicAuthentication)
	permission_classes = (IsAdminUser,)
	queryset = Queue.objects.all()
	serializer_class = serializers.QueueSerializer
	def list_new_queue(self):
		latest_queue = self.get_object()
		return self.queryset.filter(date_created__gt=latest_queue.date_created).filter(service=latest_queue.service)
	def retrieve(self, request, *args, **kwargs):
		retrieve_ctx = super().retrieve(request, *args, **kwargs)
		retrieve_ctx.data = list()
		for queue in self.list_new_queue():
			new_queues = self.serializer_class(queue).data
			retrieve_ctx.data.append(new_queues)
		return retrieve_ctx
