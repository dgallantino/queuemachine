from queue_app.models import Service, Queue
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.forms.models import model_to_dict
from django.views.generic import ListView, DetailView
from django.http import JsonResponse

# Create your views here.

class IndexView(LoginRequiredMixin, ListView):
	login_url = '/accounts/login/'
	template_name ='queue_app/index.html'
	model = Service

#@login_required
def print_ticket(request, service_id):
	if request.user.is_authenticated:
		try :
			service = Service.objects.get(pk=service_id)
			last_queue = Queue.objects.last_queue_by_service(service)
			next_queue = Queue(service = service, number = last_queue.number +1)
			next_queue.save()
			return_json_obj = model_to_dict(next_queue)
			return JsonResponse(return_json_obj)
		except Service.DoesNotExist :
			return JsonResponse({'Error':'Service not found'})
		except IndexError :
			next_queue = Queue(service = service, number = 1)
			next_queue.save()
			return_json_obj = model_to_dict(next_queue)
			return JsonResponse(return_json_obj)
		except Exception as err:
			return JsonResponse({	'Error': 'Unexpected Error', 
									'ErrorMsg': str(err)})
	else:
		return JsonResponse({'Error':'This user is not authenticated'})

