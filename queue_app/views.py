from queue_app.models import Service, Queue
from queue_app.serializers import QueueSerializer
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.forms.models import model_to_dict
from django.views.generic import ListView, DetailView
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response

class IndexView(LoginRequiredMixin, ListView):
	login_url = '/accounts/login/'
	template_name ='queue_app/index.html'
	model = Service
	
class PrintTicket(LoginRequiredMixin, DetailView):
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

class PrintTicketApi(APIView):
	http_method_names=['post']
	def post(self, request, pk):
		return Response([request,pk])
'''Function Based Approach'''
def add_next_queue(p_service):
	try:
		last_queue = Queue.objects.get_last_service_queue(p_service)
		next_queue = Queue(service = p_service, number = last_queue.number +1)
	except IndexError:#no queues is created yet
		next_queue = Queue(service = p_service, number = 1)
	next_queue.save()
	return next_queue
@login_required
def print_ticket(request, service_id):
	if request.user.is_authenticated:
		try:
			next_queue = add_next_queue(service_id)
			return_json_obj = model_to_dict(next_queue)
			return_json_obj['service']=next_queue.service
			return JsonResponse(return_json_obj)
		except Service.DoesNotExist:
			return JsonResponse({'Error':'Service not found'})
		except Exception as err:
			return JsonResponse({	'Error': 'Unexpected Error',
									'ErrorMsg': str(err)})
	else:
		return JsonResponse({'Error':'This user is not authenticated'})
