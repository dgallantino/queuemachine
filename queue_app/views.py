from queue_app import forms, models
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic import ListView, DetailView, TemplateView
from django.urls.base import reverse_lazy


#todos: 
#filter everything based on user.organization

class IndexView(TemplateView):
	template_name = 'queue_app/index.html'
	
	def get(self, request, *args, **kwargs):
		return TemplateView.get(self, request, *args, **kwargs)

class SignUp(CreateView):
	form_class = forms.CustomUserCreationForm
	success_url = reverse_lazy('queue:print_ticket_url')
	template_name = 'registration/signup.html'

'''
Machine Display view
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
	def get_success_url(self):
		return reverse_lazy('queue:print_ticket_url', kwargs={'pk':self.object.id})
	def form_invalid(self, form):
		return CreateView.form_invalid(self, form)
	
#booking entry is updated right before printing
#so the number is sorted based on time it was printed
class PrintBookingTicket(LoginRequiredMixin, UpdateView):
	login_url = '/queuemachine/login/'
	template_name ='queue_app/machine/placeholder_ticket.html'
	object_name = 'queue'
	form_class=forms.QueueModelForms
	def get_queryset(self):
		services = self.request.user.organization.services.all()
		return models.Queue.objects.services_filter(services).booking()
	def get_success_url(self):
		return reverse_lazy('queue:print_ticket_url', kwargs={'pk':self.object.id})
	def form_invalid(self, form):
		return UpdateView.form_invalid(self, form)
	
class PrintTicket(LoginRequiredMixin, DetailView):
	login_url = '/queuemachine/login/'
	template_name ='queue_app/machine/placeholder_ticket.html'
	object_name = 'queue'
	model=models.Queue
# 	def get_queryset(self):
# 		services = self.request.user.organization.services.all()
# 		return models.Queue.objects.services_filter(iterable=services).printed()

class BookingList(LoginRequiredMixin, ListView):
	login_url = '/queuemachine/login/'
	template_name ='queue_app/machine/placeholder_queues.html'
	context_object_name = 'queues'
	def get_queryset(self):
		services = self.request.user.organization.services.all()
		return models.Queue.objects.services_filter(services).booking().not_printed()
	
class BookingListUpdate(LoginRequiredMixin, DetailView):
	login_url = '/queuemachine/login/'
	template_name ='queue_app/machine/placeholder_queues.html'
	context_object_name = 'queues'
	def get_queryset(self):
		services = self.request.user.organization.services.all()
		return models.Queue.objects.services_filter(services).booking().not_printed()
	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['queues']=self.get_queryset().filter(
			date_created__gt=self.object.date_created
			).get_not_printed()
		return context
	
'''
Manager...
...to manage queue like calling, delete and shit
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
	context_object_name = 'services'
	def get_queryset(self):
		return self.request.user.organization.services.all()
	
class UserLookupView(LoginRequiredMixin, ListView):
	lodin_url = '/queuemachine/login/'
	template_name = 'queue_app/manager/user_lookup.html'
	context_object_name= 'users'
	
	
class AddBookingQueue(LoginRequiredMixin, SuccessMessageMixin, CreateView):
	login_url = '/queuemachine/login/'
	template_name = 'queue_app/manager/add_booking_form.html'
	model = models.Queue
	form_class=forms.QueueModelForms
	success_message = "booking was created"
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
	def form_valid(self, form):
		return SuccessMessageMixin.form_valid(self, form)
	def form_invalid(self, form):
		return CreateView.form_invalid(self, form)
	#end-debug_code
	
class QueuePerService(LoginRequiredMixin, DetailView):
	login_url = '/queuemachine/login/'
	template_name='queue_app/manager/placeholder_queues.html'
	model = models.Service
	def get_context_data(self, **kwargs):
		context= super().get_context_data(**kwargs)
		context['queues'] = self.object.queues.get_today_list()
		return context
