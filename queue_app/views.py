from queue_app import forms, models
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.views.generic.edit import CreateView
from django.views.generic import ListView, DetailView, TemplateView
from django.urls.base import reverse_lazy

class IndexView(TemplateView):
	template_name = 'queue_app/index.html'
	
	def get(self, request, *args, **kwargs):
		return TemplateView.get(self, request, *args, **kwargs)

class SignUp(CreateView):
	form_class = forms.CustomUserCreationForm
	success_url = reverse_lazy('queue:print_ticket_url')
	template_name = 'registration/signup.html'

'''
Machine Display
as in display that ticket booth uses
component
- MachineDisplay (page)
	-> GET: list of services
	-> POST: Create new queue
- AddQueueFormView
- QueueObjectDetail
'''

#Implpmptation using form and normal html request
class MachineDisplay(LoginRequiredMixin, CreateView):
	login_url = '/queuemachine/login/'
	template_name ='queue_app/machine/machine.html'
	model = models.Queue
	form_class=forms.QueueModelForms
	def get_context_data(self, **kwargs):
		kwargs['services'] = models.Service.objects.all()
		return super().get_context_data(**kwargs)
	def get_success_url(self):
		return reverse_lazy('queue:print_ticket_url', kwargs={'pk':self.object.id})
	
class PrintTicket(LoginRequiredMixin, DetailView):
	login_url = '/queuemachine/login/'
	template_name ='queue_app/machine/placeholder_ticket.html'
	object_name = 'queue'
	def get_queryset(self):
		return models.Queue.objects.get_today_list()

class BookingList(LoginRequiredMixin, ListView):
	login_url = '/queuemachine/login/'
	template_name ='queue_app/machine/placeholder_queues.html'
	context_object_name = 'queues'
	def get_queryset(self):
		return models.Queue.objects.get_nonbooking()
	
class BookingListUpdate(LoginRequiredMixin, DetailView):
	login_url = '/queuemachine/login/'
	template_name ='queue_app/machine/placeholder_queues.html'
	context_object_name = 'queues'
	def get_queryset(self):
		return models.Queue.objects.get_nonbooking()
	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['queues']=self.get_queryset().filter(
			date_created__gt=self.object.date_created)
		return context
	
'''
Manager...
...to manage queue like calling delete and shit
componen:
- Manager Display
	-> Context: list of services(with its related queues)
- AddBookingQueue
	-> GET: add booking form
	-> POST: booking submition
'''
class ManagerDisplay(LoginRequiredMixin, ListView):
	login_url = '/queuemachine/login/'
	template_name='queue_app/manager/manager.html'
	model = models.Service
	context_object_name = 'Services'
	
class AddBookingQueue(LoginRequiredMixin, SuccessMessageMixin, CreateView):
	login_url = '/queuemachine/login/'
	template_name = 'queue_app/manager/add_booking_form.html'
	model = models.Queue
	form_class=forms.QueueModelForms
	success_message = "%(customer)s booking was created"
	def get_success_url(self):
		return reverse_lazy('queue:add_booking_url')
	#debug_code
	def post(self, request, *args, **kwargs):
		debug= super().post(request, *args, **kwargs)
		return debug
	def get_context_data(self, **kwargs):
		debug=super().get_context_data( **kwargs)
		return debug
	def get(self, request, *args, **kwargs):
		debug= super().get(request, *args, **kwargs)
		return debug
	#end-debug_code
	
class QueuePerService(LoginRequiredMixin, DetailView):
	login_url = '/queuemachine/login/'
	template_name='queue_app/manager/placeholder_queues.html'
	model = models.Service
	def get_context_data(self, **kwargs):
		context= super().get_context_data(**kwargs)
		context['queues'] = self.object.queues.get_today_list()
		return context
