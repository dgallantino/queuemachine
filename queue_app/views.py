from io import BytesIO
import calendar
import time
import math
import re
import requests

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic import ListView, DetailView, TemplateView, View
from django.urls.base import reverse_lazy
from django.views.generic.base import RedirectView
from django.views.generic.detail import SingleObjectMixin
from django.http.response import HttpResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required

from dal import autocomplete

from gtts import gTTS
from gtts_token.gtts_token import Token

from queue_app import forms, models
from queue_app import constants as const

def _patch_faulty_function(self):
	if self.token_key is not None:
		return self.token_key

	timestamp = calendar.timegm(time.gmtime())
	hours = int(math.floor(timestamp / 3600))

	results = requests.get("https://translate.google.com/")
	tkk_expr = re.search("(tkk:*?'\d{2,}.\d{3,}')", results.text).group(1)
	tkk = re.search("(\d{5,}.\d{6,})", tkk_expr).group(1)

	a , b = tkk.split('.')

	result = str(hours) + "." + str(int(a) + int(b))
	self.token_key = result
	return result

Token._get_token_key = _patch_faulty_function


'''
Bases
'''
class QueueAppLoginMixin(LoginRequiredMixin):
	login_url = reverse_lazy('login')

class BaseBoothListView(QueueAppLoginMixin,ListView):
	context_object_name = 'booths'
	def get_queryset(self):
		return (
			models.CounterBooth.objects
			.filter(organization=self.request.session.get(const.IDX.ORG,{}).get('id'))
		)

class OrganizationSetter(View):
	def get(self, request, *args, **kwargs):
		if not request.session.get(const.IDX.ORG):
			if request.user.organization.all().count() > 1:
				messages.add_message(
					request=request,
					level=messages.WARNING,
					message='Anda mempunyai beberapa organisasi, harap pilih salah satu melalui manager',
					fail_silently=True,
				)
			else:
				request.session[const.IDX.ORG] = request.user.organization.last().to_flat_dict()
		return super(OrganizationSetter, self).get( request, *args, **kwargs)

'''
No signins views
'''
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
- MachineDisplayView (page)
	-> GET: list of services
	-> POST: Create new queue
- AddQueueFormView
- QueueObjectDetail
'''

#Implpmptation using form and normal html request
#CreateView to create new normal Queue
#context['services'] to list availale services
class MachineDisplayView(
		QueueAppLoginMixin,
		OrganizationSetter,
		CreateView,
	):
	template_name ='queue_app/machine/machine.html'
	model = models.Queue
	form_class=forms.AddQueueModelForms
	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context[const.TEMPLATE.SERVICES] = (
			models.Service.objects
			.org_filter(
				self.request.session.get(const.IDX.ORG,{}).get('id')
			)
		)
		return context
	def get_success_url(self):
		return reverse_lazy('queue:print_ticket_url', kwargs={'pk':self.object.id})

#booking entry is updated right before printing
#so the number is sorted based on time it was printed
#UpdateView class is there to handle booking queue
class PrintTicketView(QueueAppLoginMixin, DetailView, UpdateView,):
	template_name ='queue_app/machine/placeholder_ticket.html'
	context_object_name = const.TEMPLATE.QUEUE
	form_class=forms.PrintQueueModelForms
	def get_queryset(self):
		services =(
			models.Service.objects
			.org_filter(
				self.request.session.get(const.IDX.ORG,{}).get('id')
			)
		)
		return (
			models.Queue.objects
			.today_filter()
			.services_filter(services)
		)

	def get_success_url(self):
		return reverse_lazy('queue:print_ticket_url', kwargs={'pk':self.object.id})

#ListView list all booking queue
#SingleObjectMixin get Queue id in url and list the new queue after that one
class BookingQueueListView(
		QueueAppLoginMixin,
		SingleObjectMixin,
		ListView,
	):
	template_name ='queue_app/machine/placeholder_queues.html'
	def get_object(self, queryset=None):
		if self.kwargs.get(self.pk_url_kwarg):
			return super().get_object( queryset=queryset)
		return None

	def get(self, request, *args, **kwargs):
		services =(
			models.Service.objects
			.filter(
				organization=self.request.session.get(const.IDX.ORG,{}).get('id')
			)
		)

		self.object = self.get_object(
			models.Queue.objects
			.today_filter()
			.services_filter(services)
			.is_printed(False)
			.is_booking(True)
		)
		return super(BookingQueueListView,self).get( request, *args, **kwargs)

	def get_queryset(self):
		services = (
			models.Service.objects
			.org_filter(
				self.request.session.get(const.IDX.ORG,{}).get('id')
			)
		)
		qs = (
			models.Queue.objects
			.today_filter()
			.services_filter(services)
			.is_booking(True)
			.is_printed(False)
		)
		if self.kwargs.get(self.pk_url_kwarg):
			qs = (
				qs
				.filter(date_created__gt=self.object.date_created)
			)
		return qs

	def get_context_data(self, **kwargs):
		context = super(BookingQueueListView, self).get_context_data(**kwargs)
		context[const.TEMPLATE.QUEUES] = self.object_list
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
- LookUps: Django auto complete views,
	to list all result of auto complete queries for forms
'''
class ManagerDisplayView(QueueAppLoginMixin, OrganizationSetter, ListView):
	template_name='queue_app/manager/manager.html'
	context_object_name = const.TEMPLATE.SERVICES
	def get_queryset(self):
		return (
			models.Service.objects
			.org_filter(self.request.session.get(const.IDX.ORG,{}).get('id'))
		)

class UserLookupView(
		QueueAppLoginMixin,
		autocomplete.Select2QuerySetView,
	):
	def get_queryset(self):
		query_set = (
			models.User.objects
			.filter(
				organization=(self.request.session.get(const.IDX.ORG,{}).get('id'))
			)
		)
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

class ServiceLookupView(
		QueueAppLoginMixin,
		autocomplete.Select2QuerySetView,
	):
	def get_queryset(self):
		query_set= (
			models.Service.objects
			.org_filter(
				self.request.session.get(const.IDX.ORG,{}).get('id')
			)
		)
		if self.q:
			qs1 = query_set.filter(name__startswith=self.q)
			qs2 = query_set.filter(desc__startswith=self.q)
			query_set = qs1.union(qs2)
		return query_set

class ManagerBoothListView(BaseBoothListView):
	template_name = 'queue_app/manager/booth_list.html'

class BoothToSession(
		QueueAppLoginMixin,
		SingleObjectMixin,
		RedirectView,
	):
	http_method_names = ['get',]
	url = reverse_lazy("queue:manager_url")
	def get_queryset(self):
		return (
			models.CounterBooth.objects
			.filter(organization=self.request.session.get(const.IDX.ORG,{}).get('id'))
		)
	def get_redirect_url(self, *args, **kwargs):
		CounterBooth_object=self.get_object()
		if CounterBooth_object:
			self.request.session[const.IDX.BOOTH] = CounterBooth_object.to_flat_dict()
		return super().get_redirect_url(*args,**kwargs)

class OrganizationListView(QueueAppLoginMixin,ListView):
	template_name = 'queue_app/manager/organization_list.html'
	context_object_name = const.TEMPLATE.ORGS
	def get_queryset(self):
		return self.request.user.organization.all()

class OrganizationToSession(
		QueueAppLoginMixin,
		SingleObjectMixin,
		RedirectView,
	):
	http_method_names = ['get',]
	url = reverse_lazy('queue:manager_url')
	def get_queryset(self):
		return self.request.user.organization.all()
	def get_redirect_url(self, *args, **kwargs):
		self.request.session[const.IDX.ORG] = self.get_object().to_flat_dict()
		return super().get_redirect_url(*args, **kwargs)

class AddCustomerView(
		LoginRequiredMixin,
		SuccessMessageMixin,
		CreateView,
	):
	login_url = reverse_lazy('login')
	success_url = reverse_lazy('queue:add_customer_url')
	template_name = 'queue_app/manager/add_customer_form.html'
	model = models.User
	form_class=forms.CustomerCreationForm
	success_message = "Customer data creation was successfull"

class AddBookingQueueView(
		LoginRequiredMixin,
		SuccessMessageMixin,
		CreateView,
	):
	login_url = reverse_lazy('login')
	success_url = reverse_lazy('queue:add_booking_url')
	template_name = 'queue_app/manager/add_booking_form.html'
	model = models.Queue
	form_class=forms.AddBookingQueuemodelForms
	success_message = "booking was created"

#SingleObjectMixin get Service object from url kwargs
#ListView list all Queues from that service
#todos: exetend a basic Queue list view(?)
class QueuePerServiceView(
		QueueAppLoginMixin,
		ListView,
		SingleObjectMixin,
	):
	template_name='queue_app/manager/placeholder_queues.html'
	def get(self, request, *args, **kwargs):
		self.object= self.get_object(
			models.Service.objects
			.org_filter(self.request.session.get(const.IDX.ORG,{}).get('id'))
		)
		return super().get( request, *args, **kwargs)

	def get_context_data(self, **kwargs):
		context= super().get_context_data(**kwargs)
		context['service'] = self.object
		context['queues'] = self.object_list
		return context

	def get_queryset(self):
		qs = (
			self.object.queues
			.today_filter()
			.is_booking(self.request.GET.get('booking'))
			.is_printed(True)
			.is_called(False)
			.order_by('print_datetime')
		)
		return qs

class CallQueueView(LoginRequiredMixin,UpdateView):
	login_url = reverse_lazy('login')
	success_url = reverse_lazy('queue:manager_url')
	form_class = forms.CallQueueModelForms
	model = models.Queue
	template_name = 'queue_app/manager/test_form_template.html'

@login_required
def playAudioFile(request):
	queue = get_object_or_404(
		models.Queue,
		pk = request.GET.get('queue')
	)
	booth = get_object_or_404(
		models.CounterBooth,
		pk = request.session.get(const.IDX.BOOTH,{}).get('id')
	)
	if (queue and booth):
		tts_string = "antrian "+queue.character+" "+str(queue.number)+" ke "+booth.spoken_name
		mp3_fp = BytesIO()
		tts = gTTS(tts_string, 'id')
		tts.write_to_fp(mp3_fp)
		response = HttpResponse()
		response.write(mp3_fp.getvalue())
		response['Content-Type'] ='audio/mp3'
		response['Content-Length'] =mp3_fp.getbuffer().nbytes
		mp3_fp.close()
		return response
	return HttpResponseBadRequest

'''
Queue info boards
Displaying the list of remaining queue
and the current served queue
hope i got this right
'''
#context : booth list
class InfoBoardMainView(BaseBoothListView,OrganizationSetter):
	template_name = "queue_app/info_board/info_board.html"
	def get_queryset(self):
		return (
			models.CounterBooth.objects
			.filter(organization=self.request.session.get(const.IDX.ORG,{}).get('id'))
		)

#context : booth detail
class InfoBoardBoothDetailView(QueueAppLoginMixin,DetailView):
	template_name = "queue_app/info_board/booth_list.html"
	model = models.CounterBooth
	context_object_name = "booth"

class InfoBoardQueuePerService(QueuePerServiceView):
	template_name = "queue_app/info_board/info_board.html"

#context : all queue in loged in user's	groups
class InfoBoardQueueListView(QueueAppLoginMixin, ListView):
	template_name = "queue_app/info_board/placeholder_queues.html"
	context_object_name = "queues"
	def get_queryset(self):
		services =(
			models.Service.objects
			.org_filter(self.request.user.groups.all())
		)
		return (
			models.Queue.objects
			.today_filter()
			.services_filter(services)
			.is_printed(True)
			.is_called(False)
			.order_by('print_datetime')
		)
