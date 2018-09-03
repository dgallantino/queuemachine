from queue_app.models import Service
from queue_app.serializers import QueueSerializer
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response

class MachineDisplay(LoginRequiredMixin, ListView):
	login_url = '/accounts/login/'
	template_name ='queue_app/index.html'
	model = Service
	
class PrintTicketView(LoginRequiredMixin, DetailView):
	template_name ='queue_app/test.html'
	model = Service
	http_method_names = ['get']
	object_name = 'queue';
	def add_next_queue(self, service):
		last_queue = service.queues.last()
		if last_queue:
			next_queue = service.queues.create(
				number = last_queue.number + 1
				)
			return next_queue
		next_queue = service.queues.create(number = 1)	
		return next_queue
	def get(self, request, *args, **kwargs):		
		return JsonResponse(QueueSerializer(self.add_next_queue(self.get_object())).data)
	
class IndexView(ListView):
	def get(self, request, *args, **kwargs):
		return ListView.get(self, request, *args, **kwargs)
'''
next
'''
class PrintTicketApi(APIView):
	http_method_names=['post','get']
	def post(self, request):
		return Response([request,])