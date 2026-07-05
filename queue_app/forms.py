'''
Created on Oct 1, 2018

@author: gallantino
'''
from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, PasswordChangeForm
from queue_app import models
from dal import autocomplete
from datetime import datetime

from django.utils.translation import gettext_lazy as _

from queue_app.services import QueueService, UserService


class BaseMedia:
    css = {
        'all': (
            'queue_app/bootstrap/css/bootstrap.min.css',
            'queue_app/font-awesome/css/font-awesome.min.css',
            'queue_app/jquery-ui/jquery-ui.min.css',
            'queue_app/jquery-timepicker/jquery.timepicker.min.css',
        ),
    }
    js = (
        'queue_app/jquery-ui/jquery-ui.min.js',
        'queue_app/jquery-timepicker/jquery.timepicker.min.js',
    )


class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = models.User
        fields = ('username', 'password1', 'password2',)


class CustomUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = models.User


class CustomerCreationForm(CustomUserCreationForm):
    def __init__(self, *args, **kwargs):
        super(CustomerCreationForm, self).__init__(*args, **kwargs)
        self.fields['password1'].required = False
        self.fields['password2'].required = False

    def save(self, commit=True):
        new_customer = super(CustomerCreationForm, self).save(commit=False)
        new_customer.username = self.cleaned_data.get('first_name') + self.cleaned_data.get('last_name')
        new_customer.set_unusable_password()
        if commit:
            UserService.save_customer(new_customer, save_m2m=self.save_m2m)
        return new_customer

    class Meta(CustomUserCreationForm.Meta):
        fields = (
            'first_name',
            'last_name',
            'email',
            'phone',
            'organization',
        )

        labels = {
            'first_name': _('first name'),
            'last_name': _('last name'),
            'email': _('email address'),
            'phone': _('phone'),
            'organization': _('organization')
        }

        widgets = {
            'organization': autocomplete.ModelSelect2Multiple(
                url='queue:manager:organization_autocomplete',
                attrs={
                    'id': 'organization',
                    'data-placeholder': _('organization'),
                },
            ),
        }

    class Media:
        css = {
            'all': (
                'queue_app/bootstrap/css/bootstrap.min.css',
                'queue_app/jquery-ui/jquery-ui.min.css',
                'queue_app/core/css/manager-form.css'
            ),
        }
        js = (
            'queue_app/jquery-ui/jquery-ui.min.js',
        )


class EmployeeChangeForm(CustomUserChangeForm):
    # def __init__(self, *args, **kwargs):
    #     super(EmployeeChangeForm,self).__init__(*args, **kwargs)
    class Meta(CustomUserChangeForm.Meta):
        fields = (
            'first_name',
            'last_name',
            'username',
            'email',
            'phone',
            'password',
        )

        labels = {
            'first_name': _('first name'),
            'last_name': _('last name'),
            'username': _('user name'),
            'email': _('email address'),
            'phone': _('phone'),
        }

    class Media:
        css = {
            'all': (
                'queue_app/bootstrap/css/bootstrap.min.css',
                'queue_app/jquery-ui/jquery-ui.min.css',
                'queue_app/core/css/manager-form.css'
            ),
        }
        js = (
            'queue_app/jquery-ui/jquery-ui.min.js',
        )


class EmployeePasswordChangeForm(PasswordChangeForm):
    class Media:
        css = {
            'all': (
                'queue_app/bootstrap/css/bootstrap.min.css',
                'queue_app/core/css/manager-form.css'
            ),
        }


class QueueModelBaseForms(forms.ModelForm):
    booking_time = forms.TimeField(
        label=_("booking time"),
        initial=datetime.now(),
        required=False,
        widget=forms.TimeInput(
            format='%H:%M',
            attrs={
                'id': 'booking-time',
                'class': 'input-field',
            },
        ),
    )

    booking_date = forms.DateField(
        label=_("booking date"),
        initial=datetime.now(),
        required=False,
    )

    class Meta:
        model = models.Queue
        fields = '__all__'

        widgets = {
            'service': autocomplete.ModelSelect2(
                url='queue:manager:service_autocomplete',
                attrs={
                    'id': 'service',
                    'data-placeholder': _('service'),
                    'data-minimum-input-length': 1,
                },
            ),
            'customer': autocomplete.ModelSelect2(
                url='queue:manager:user_autocomplete',
                attrs={
                    'id': 'customer',
                    'data-placeholder': _('customer'),
                    'data-minimum-input-length': 3,
                },
            ),
        }


    def save(self, commit=True):
        # get models.Queue isntance to create or edit
        new_queue = super(QueueModelBaseForms, self).save(commit=False)
        if self.cleaned_data.get('is_booking', False):
            try:
                # get booking data
                new_queue.booking_datetime = datetime.combine(
                    self.cleaned_data.pop('booking_date'),
                    self.cleaned_data.pop('booking_time')
                )
            except Exception:
                raise Exception('Failed to create booking')

        should_print = self.cleaned_data.pop('is_printed', False)
        if commit:
            if should_print:
                new_queue.is_printed = False
            new_queue.save()
            if should_print:
                new_queue = QueueService.assign_ticket_number(new_queue)
        return new_queue


class AddQueueModelForms(QueueModelBaseForms):
    class Meta(QueueModelBaseForms.Meta):
        fields = ('service', 'is_printed',)


class AddBookingQueuemodelForms(QueueModelBaseForms):
    class Meta(QueueModelBaseForms.Meta):
        fields = ('service', 'customer', 'is_booking')


class PrintQueueModelForms(QueueModelBaseForms):
    class Meta(QueueModelBaseForms.Meta):
        fields = ('is_printed',)


class FinishQueueModelForms(QueueModelBaseForms):
    class Meta(QueueModelBaseForms.Meta):
        fields = ('is_finished',)

    def save(self, commit=True):
        if commit:
            return QueueService.finish_queue(self.instance)
        return super().save(commit=False)


class CallQueueModelForms(QueueModelBaseForms):
    class Meta(QueueModelBaseForms.Meta):
        fields = ('is_called', 'counter_booth')

    def save(self, commit=True):
        counter_booth = self.cleaned_data.get('counter_booth')
        if commit:
            return QueueService.call_queue(self.instance, counter_booth)
        return super().save(commit=False)


class MoveQueueModelForms(QueueModelBaseForms):
    class Meta(QueueModelBaseForms.Meta):
        fields = ('service',)

    def save(self, commit=True):
        target_service = self.cleaned_data.get('service')
        if commit:
            return QueueService.move_queue(self.instance, target_service)
        return super().save(commit=False)
