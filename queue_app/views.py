from queue_app import forms, models
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic import ListView, DetailView, TemplateView
from django.urls.base import reverse_lazy
from dal import autocomplete
from django.views.generic.base import RedirectView
from django.views.generic.detail import SingleObjectMixin



#todos: 
#work on the manager

class IndexView(TemplateView):
	template_name = 'queue_app/index.html'

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
	form_class=forms.AddQueueModelForms
	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['services'] = models.Service.objects.group_filter(self.request.user.groups.all())
		return context
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
	form_class=forms.BookingQueueForms
	#models = models.Queue would sufice
	#probably
	def get_queryset(self):
		services =( 
			models.Service.objects
			.group_filter(self.request.user.groups.all())
		)
		return (
			models.Queue.objects
			.today_filter()
			.services_filter(services)
			.is_booking(True)
		)
		
	def get_success_url(self):
		return reverse_lazy('queue:print_ticket_url', kwargs={'pk':self.object.id})
	
class PrintTicket(LoginRequiredMixin, DetailView):
	login_url = '/queuemachine/login/'
	template_name ='queue_app/machine/placeholder_ticket.html'
	object_name = 'queue'
	model=models.Queue

class BookingList(LoginRequiredMixin, ListView):
	login_url = '/queuemachine/login/'
	template_name ='queue_app/machine/placeholder_queues.html'
	context_object_name = 'queues'
	
	def get_queryset(self):
		services = (
			models.Service.objects
			.group_filter(self.request.user.groups.all())
		)
		return (
			models.Queue.objects
			.today_filter()
			.services_filter(services)
			.is_booking(True)
			.is_printed(False)
		)
	
class BookingListUpdate(LoginRequiredMixin, DetailView):
	login_url = '/queuemachine/login/'
	template_name ='queue_app/machine/placeholder_queues.html'
	context_object_name = 'queues'
	
	def get_queryset(self):
		services = (
			models.Service.objects
			.group_filter(self.request.user.groups.all())
		)
		return (
			models.Queue.objects
			.today_filter()
			.services_filter(services)
			.is_booking(True)
			.is_printed(False)
		)	
	
	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['queues']=(
			self.get_queryset()
			.filter(date_created__gt=self.object.date_created)
			.is_printed(False)
		)
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
		return models.Service.objects.group_filter(self.request.user.groups.all())
	
class UserLookupView(LoginRequiredMixin, autocomplete.Select2QuerySetView):
	login_url = '/queuemachine/login/'
	def get_queryset(self):
		query_set = models.User.objects.filter(groups__in=self.request.user.groups.all())
		if self.q:
			qs1 = query_set.filter(username__startswith=self.q)
			qs2 = query_set.filter(first_name__startswith=self.q)
			qs3 = query_set.filter(last_name__startswith=self.q)
			query_set = qs1.union(qs2,qs3)
		return query_set
	
	def get_result_label(self, result):
		return result.get_full_name()
	def get_selected_result_label(self, result):
		return result.get_full_name()
	
class ServiceLookupView(LoginRequiredMixin, autocomplete.Select2QuerySetView):
	logi_url = '/queuemachine/login/'
	def get_queryset(self):
		query_set= models.Service.objects.filter(groups__in=self.request.user.groups.all())
		if self.q:
			qs1 = query_set.filter(name__startswith=self.q)
			qs2 = query_set.filter(desc__startswith=self.q)
			query_set = qs1.union(qs2)
		return query_set
	
class BoothListView(LoginRequiredMixin,ListView):
	login_url = reverse_lazy('login')
	template_name = 'queue_app/manager/booth_list.html'
	context_object_name = 'booths'
	def get_queryset(self):
		return (
			models.CounterBooth.objects
			.filter(groups__in=self.request.user.groups.all())
		)

class BoothToSession(LoginRequiredMixin,SingleObjectMixin, RedirectView):
	login_url = reverse_lazy('login')
	http_method_names = ['get',]
	url = reverse_lazy("queue:manager_url")
	def get_queryset(self):
		return (
			models.CounterBooth.objects
			.filter(groups__in=self.request.user.groups.all())
		)
	def get_redirect_url(self, *args, **kwargs):
		CounterBooth_object=self.get_object()
		if CounterBooth_object:
			CounterBooth_dict = {'name':CounterBooth_object.name,'id':str(CounterBooth_object.id)}
			self.request.session['CounterBooth'] = CounterBooth_dict
		return super().get_redirect_url(*args,**kwargs)
	
class AddCustomerView(LoginRequiredMixin,SuccessMessageMixin, CreateView):
	login_url = '/queuemachine/login/'
	template_name = 'queue_app/manager/add_customer_form.html'
	model = models.User
	form_class=forms.CustomUserCreationForm
	success_message = "Customer data creation was successfull"
	def get_success_url(self):
		return reverse_lazy('queue:add_customer_url')
	
class AddBookingQueueView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
	login_url = '/queuemachine/login/'
	template_name = 'queue_app/manager/add_booking_form.html'
	model = models.Queue
	form_class=forms.BookingQueueForms
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
