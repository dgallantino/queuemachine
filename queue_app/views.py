from io import BytesIO
import calendar
import logging
import time
import math
import re
import requests

from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin, AccessMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic import ListView, DetailView, TemplateView, View
from django.urls.base import reverse_lazy
from django.views.generic.base import RedirectView
from django.views.generic.detail import SingleObjectMixin
from django.http.response import HttpResponse
from django.http import Http404, HttpResponseBadRequest
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.contrib.auth.views import PasswordChangeView

from dal import autocomplete

from gtts import gTTS
from gtts_token.gtts_token import Token

from queue_app import forms, models
from queue_app import constants as const
from queue_app.sounds.announcement import destination_key_for_booth
from queue_app.sounds.compose import compose_queue_call


def _patch_faulty_function(self):
    if self.token_key is not None:
        return self.token_key

    timestamp = calendar.timegm(time.gmtime())
    hours = int(math.floor(timestamp / 3600))

    results = requests.get("https://translate.google.com/")
    tkk_expr = re.search("(tkk:*?'\d{2,}.\d{3,}')", results.text).group(1)
    tkk = re.search("(\d{5,}.\d{6,})", tkk_expr).group(1)

    a, b = tkk.split('.')

    result = str(hours) + "." + str(int(a) + int(b))
    self.token_key = result
    return result


Token._get_token_key = _patch_faulty_function

'''
Bases
'''


def session_org_id(request):
    return request.session.get(const.IDX.ORG, {}).get('id')


def user_has_org_access(user, org_id):
    if not org_id:
        return False
    return user.organization.filter(pk=org_id).exists()


def require_session_org(request):
    """Return the session org id if the user may access it, else None."""
    org_id = session_org_id(request)
    if user_has_org_access(request.user, org_id):
        return org_id
    return None


def get_org_queue(request, queue_pk):
    org_id = require_session_org(request)
    if not org_id:
        raise Http404
    return get_object_or_404(models.Queue.objects.for_org(org_id), pk=queue_pk)


def get_session_booth(request):
    org_id = require_session_org(request)
    booth_id = request.session.get(const.IDX.BOOTH, {}).get('id')
    if not org_id or not booth_id:
        raise Http404
    return get_object_or_404(models.CounterBooth.objects.for_org(org_id), pk=booth_id)


class QueueAppLoginMixin(LoginRequiredMixin):
    pass


class OrgScopedMixin:
    def get_org_id(self):
        return require_session_org(self.request)

    def get_org_services(self):
        return models.Service.objects.for_org(self.get_org_id())

    def get_org_queues(self):
        return models.Queue.objects.for_org(self.get_org_id())

    def get_org_booths(self):
        return models.CounterBooth.objects.for_org(self.get_org_id())

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['org_id'] = self.get_org_id()
        return kwargs


class OrgScopedQueueMixin(OrgScopedMixin):
    def get_queryset(self):
        return self.get_org_queues()


class BaseBoothListView(QueueAppLoginMixin, OrgScopedMixin, ListView):
    context_object_name = const.TEMPLATE.BOOTHS

    def get_queryset(self):
        return self.get_org_booths()


class SessionInitializer(View):
    def get(self, request, *args, **kwargs):
        # set default language to indonesia
        # if not request.COOKIES.get(settings.LANGUAGE_COOKIE_NAME):
        # 	translation.activate(const.LANG.ID)
        # 	response.set_cookie(settings.LANGUAGE_COOKIE_NAME, const.LANG.ID)
        # set organization if user only have one
        if not request.session.get(const.IDX.ORG):
            org_count = request.user.organization.all().count()
            if org_count > 1:
                messages.add_message(
                    request=request,
                    level=messages.WARNING,
                    message=_('you have more than one organization, please choose one'),
                    fail_silently=True,
                )
            elif org_count == 0:
                messages.add_message(
                    request=request,
                    level=messages.ERROR,
                    message=_('you are not assigned to any organization'),
                    fail_silently=True,
                )
            else:
                request.session[const.IDX.ORG] = request.user.organization.last().to_flat_dict()
        return super(SessionInitializer, self).get(request, *args, **kwargs)


'''
No signins views
'''


class IndexView(TemplateView):
    template_name = 'queue_app/index.html'


class SignUp(CreateView):
    form_class = forms.CustomUserCreationForm
    success_url = reverse_lazy('queue:index')
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


# Implementation using form and normal html request
# CreateView to create new normal Queue
# context['services'] to list available services
class MachineDisplayView(QueueAppLoginMixin, SessionInitializer, OrgScopedMixin, CreateView, ):
    template_name = 'queue_app/machine/machine.html'
    model = models.Queue
    form_class = forms.AddQueueModelForms

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context[const.TEMPLATE.SERVICES] = self.get_org_services().is_hidden(False)
        return context

    def get_success_url(self):
        return reverse_lazy('queue:machine:print', kwargs={'pk': self.object.id})

    def form_invalid(self, form):
        logger = logging.getLogger(__name__)
        logger.error('MachineDisplayView rejected queue creation: %s', form.errors)
        lines = [
            f'{field}: {"; ".join(errors)}'
            for field, errors in form.errors.items()
        ]
        return HttpResponseBadRequest('\n'.join(lines) or str(_('invalid queue request')))


# booking entry is updated right before printing
# so the number is sorted based on time it was printed
# UpdateView class is there to handle booking queue
class PrintTicketView(QueueAppLoginMixin, OrgScopedMixin, DetailView, UpdateView, ):
    template_name = 'queue_app/machine/placeholder_ticket.html'
    context_object_name = const.TEMPLATE.QUEUE
    form_class = forms.PrintQueueModelForms

    def get_queryset(self):
        return (
            self.get_org_queues()
                .today_filter()
        )

    def get_success_url(self):
        return reverse_lazy('queue:machine:print', kwargs={'pk': self.object.id})


# ListView list all booking queue
# SingleObjectMixin get Queue id in url and list the new queue after that one
class BookingQueueListView(
    QueueAppLoginMixin,
    OrgScopedMixin,
    SingleObjectMixin,
    ListView,
):
    template_name = 'queue_app/machine/placeholder_queues.html'

    def get_object(self, queryset=None):
        if self.kwargs.get(self.pk_url_kwarg):
            return super().get_object(queryset=queryset)
        return None

    def get(self, request, *args, **kwargs):
        self.object = self.get_object(
            self.get_org_queues()
                .today_filter()
                .is_printed(False)
                .is_booking(True)
        )
        return super(BookingQueueListView, self).get(request, *args, **kwargs)

    def get_queryset(self):
        qs = (
            self.get_org_queues()
                .today_filter()
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
...to manage queue like calling, delete and moving
componen:
- Manager Display
    -> Context: list of services(with its related queues)
- AddBookingQueue
    -> GET: add booking form
    -> POST: booking submission
- LookUps: Django auto complete views,
    to list all result of auto complete queries for forms
'''


class ManagerDisplayView(
    QueueAppLoginMixin,
    SessionInitializer,
    OrgScopedMixin,
    PermissionRequiredMixin,
    ListView
):
    permission_required = 'queue.can_edit'
    template_name = 'queue_app/manager/manager.html'
    context_object_name = const.TEMPLATE.SERVICES

    def get_queryset(self):
        return self.get_org_services()


class UserLookupView(
    QueueAppLoginMixin,
    OrgScopedMixin,
    autocomplete.Select2QuerySetView,
):
    def get_queryset(self):
        query_set = models.User.objects.for_org(self.get_org_id())
        if self.q:
            qs1 = query_set.filter(username__startswith=self.q)
            qs2 = query_set.filter(first_name__startswith=self.q)
            qs3 = query_set.filter(last_name__startswith=self.q)
            query_set = qs1.union(qs2, qs3)
        return query_set

    def get_result_label(self, result):
        return result.get_full_name()

    def get_selected_result_label(self, result):
        return result.get_full_name()


class ServiceLookupView(
    QueueAppLoginMixin,
    OrgScopedMixin,
    autocomplete.Select2QuerySetView,
):
    def get_queryset(self):
        queryset = self.get_org_services()
        if self.q:
            qs1 = queryset.filter(name__startswith=self.q)
            qs2 = queryset.filter(desc__startswith=self.q)
            queryset = qs1.union(qs2)
        return queryset


class OrganizationLookupView(
    QueueAppLoginMixin,
    autocomplete.Select2QuerySetView,
):
    def get_queryset(self):
        queryset = (
            models.Organization.objects
                .filter(users=self.request.user)
        )

        if self.q:
            queryset = queryset.filter(name__startswith=self.q)

        return queryset


class ManagerBoothListView(BaseBoothListView):
    template_name = 'queue_app/manager/booth_list.html'


class BoothToSession(
    QueueAppLoginMixin,
    OrgScopedMixin,
    SingleObjectMixin,
    RedirectView,
):
    http_method_names = ['get', ]
    url = reverse_lazy("queue:manager:index")

    def get_queryset(self):
        return self.get_org_booths()

    def get_redirect_url(self, *args, **kwargs):
        CounterBooth_object = self.get_object()
        if CounterBooth_object:
            self.request.session[const.IDX.BOOTH] = CounterBooth_object.to_flat_dict()
        return super().get_redirect_url(*args, **kwargs)


class OrganizationListView(QueueAppLoginMixin, ListView):
    template_name = 'queue_app/manager/organization_list.html'
    context_object_name = const.TEMPLATE.ORGS

    def get_queryset(self):
        return self.request.user.organization.all()


class OrganizationToSession(
    QueueAppLoginMixin,
    SingleObjectMixin,
    RedirectView,
):
    http_method_names = ['get', ]
    url = reverse_lazy('queue:manager:index')

    def get_queryset(self):
        return self.request.user.organization.all()

    def get_redirect_url(self, *args, **kwargs):
        self.request.session[const.IDX.ORG] = self.get_object().to_flat_dict()
        self.request.session[const.IDX.BOOTH] = None
        return super().get_redirect_url(*args, **kwargs)


class AddCustomerView(
    QueueAppLoginMixin,
    SuccessMessageMixin,
    CreateView,
):
    success_url = reverse_lazy('queue:manager:add_customer')
    template_name = 'queue_app/manager/add_customer_form.html'
    model = models.User
    form_class = forms.CustomerCreationForm
    success_message = _("customer data creation was successfull")


class AddBookingQueueView(
    QueueAppLoginMixin,
    OrgScopedMixin,
    SuccessMessageMixin,
    CreateView,
):
    success_url = reverse_lazy('queue:manager:add_booking')
    template_name = 'queue_app/manager/add_booking_form.html'
    model = models.Queue
    form_class = forms.AddBookingQueuemodelForms
    success_message = _("new booking was created")


class EditUserView(
    QueueAppLoginMixin,
    SuccessMessageMixin,
    UpdateView
):
    success_url = reverse_lazy('queue:manager:edit_user')
    template_name = 'queue_app/manager/edit_user_form.html'
    model = models.User
    form_class = forms.EmployeeChangeForm
    success_message = _("profile edit was successfull")

    def get_object(self, queryset=None):
        return self.request.user


class ChangePasswordView(
    QueueAppLoginMixin,
    SuccessMessageMixin,
    PasswordChangeView,
):
    success_url = reverse_lazy('queue:manager:index')
    template_name = 'queue_app/manager/change_password_form.html'
    success_message = _("password change was successfull")
    form_class = forms.EmployeePasswordChangeForm


# SingleObjectMixin get Service object from url kwargs
# ListView list all Queues from that service
# todos: exetend a basic Queue list view(?)
class QueuePerServiceView(
    QueueAppLoginMixin,
    OrgScopedMixin,
    ListView,
    SingleObjectMixin,
):
    template_name = 'queue_app/manager/placeholder_queues.html'

    def get(self, request, *args, **kwargs):
        self.object = self.get_object(self.get_org_services())
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context[const.TEMPLATE.SERVICE] = self.object
        context[const.TEMPLATE.QUEUES] = self.object_list
        return context

    def get_queryset(self):
        qs = (
            self.object.queues
                .today_filter()
                .is_booking(self.request.GET.get('booking'))
                .is_printed(True)
                .is_finished(False)
                .order_by('print_datetime')
        )
        return qs


class CallQueueView(QueueAppLoginMixin, OrgScopedQueueMixin, UpdateView):
    success_url = reverse_lazy('queue:manager:index')
    form_class = forms.CallQueueModelForms
    model = models.Queue


class FinishQueueView(QueueAppLoginMixin, OrgScopedQueueMixin, UpdateView):
    success_url = reverse_lazy('queue:manager:index')
    form_class = forms.FinishQueueModelForms
    model = models.Queue


class MoveQueueView(QueueAppLoginMixin, OrgScopedQueueMixin, UpdateView):
    success_url = reverse_lazy('queue:manager:index')
    form_class = forms.MoveQueueModelForms
    model = models.Queue


@login_required
def playAudioFile(request):
    queue = get_org_queue(request, request.GET.get('queue'))
    booth = get_session_booth(request)
    tts_string = "antrian " + queue.character + " " + str(queue.number) + " ke " + booth.spoken_name
    mp3_fp = BytesIO()
    tts = gTTS(tts_string, request.COOKIES.get(settings.LANGUAGE_COOKIE_NAME, const.LANG.ID))
    tts.write_to_fp(mp3_fp)
    response = HttpResponse()
    response.write(mp3_fp.getvalue())
    response['Content-Type'] = 'audio/mp3'
    response['Content-Length'] = mp3_fp.getbuffer().nbytes
    mp3_fp.close()
    return response


@login_required
def playComposedAudioFile(request):
    queue = get_org_queue(request, request.GET.get('queue'))
    booth = get_session_booth(request)
    lang_code = request.LANGUAGE_CODE
    wav_bytes, _recipe = compose_queue_call(
        queue.character,
        queue.number,
        destination_key_for_booth(booth.spoken_name),
        lang_code=lang_code,
    )
    response = HttpResponse(wav_bytes, content_type='audio/wav')
    response['Content-Length'] = len(wav_bytes)
    return response


'''
Queue info boards
Displaying the list of remaining queue
and the current served queue
hope i got this right
'''


# context : booth list
class InfoBoardMainView(SessionInitializer, BaseBoothListView):
    template_name = 'queue_app/info_board/info_board.html'


# context : booth detail
class InfoBoardBoothDetailView(QueueAppLoginMixin, OrgScopedMixin, DetailView):
    template_name = "queue_app/info_board/booth_detail.html"
    model = models.CounterBooth
    context_object_name = const.TEMPLATE.BOOTH

    def get_queryset(self):
        return self.get_org_booths()


# havent been used
class InfoBoardQueuePerService(QueuePerServiceView):
    template_name = "queue_app/info_board/info_board.html"


# context : all queues in loged in user's selected organization
class InfoBoardQueueListView(QueueAppLoginMixin, OrgScopedMixin, ListView):
    template_name = "queue_app/info_board/placeholder_queues.html"
    context_object_name = const.TEMPLATE.QUEUES

    def get_queryset(self):
        return (
            self.get_org_queues()
                .today_filter()
                .is_printed(True)
                .is_called(False)
                .order_by('print_datetime')
        )
