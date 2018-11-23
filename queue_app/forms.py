'''
Created on Oct 1, 2018

@author: gallantino
'''
from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm 
from queue_app import models
from dal import autocomplete
from datetime import datetime

class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = models.User
        fields = ('username','password1','password2',)
         
class CustomUserChangeForm(UserChangeForm):
 
    class Meta(UserChangeForm.Meta):
        model = models.User
        
#its okay to split this into multiple forms
class QueueModelBaseForms(forms.ModelForm):
    
    booking_time=forms.TimeField(
        label="Booking Time",
        initial= datetime.now(),
        required=False,
        widget=forms.TimeInput(
            format='%H:%M',
            attrs={
                'id':'booking-time',
                'class':'input-field',
            },
        ),
    )
    
    booking_date=forms.DateField(
        label="Booking Date",
        initial= datetime.now(),
        required=False,
        widget=forms.DateInput(
            format='%d-%m-%Y',
            attrs={
                'id':'booking-date',
                'class':'input-field',
            },
        ),
    )

    class Meta:
        model=models.Queue
        fields= '__all__'

        
        widgets={
            'service':autocomplete.ModelSelect2(
                url = 'queue:service_lookup_url',
                attrs={
                    'id':'service',
                    'data-placeholder': 'Service ...',
                    'data-minimum-input-length': 1,
                },
            ),
            'customer':autocomplete.ModelSelect2(
                url = 'queue:user_lookup_url',
                attrs={
                    'id':'service',
                    'data-placeholder': 'Customer ...',
                    'data-minimum-input-length': 3,
                },
            ),
        }
    
    class Media:
        css={
            'all':(
                'queue_app/bootstrap/css/bootstrap.min.css',
                'queue_app/font-awesome/css/font-awesome.min.css',
                'queue_app/core/css/manager-add_booking_form.css',
                'queue_app/jquery-ui/jquery-ui.min.css',
                'queue_app/jquery-timepicker/jquery.timepicker.min.css',
            ),
        }
        js=(
            'queue_app/jquery/jquery.js', 
            'queue_app/jquery-ui/jquery-ui.min.js',
            'queue_app/jquery-timepicker/jquery.timepicker.min.js',               
        )
        
        
    
    def save(self, commit=True):
        #get models.Queue isntance to create or edit
        new_queue = super(QueueModelBaseForms,self).save(commit=False)  
        if self.cleaned_data.get('is_booking', False):
            try:
            #get booking data
                new_queue.booking_datetime = datetime.combine(
                    self.cleaned_data.pop('booking_date'),
                    self.cleaned_data.pop('booking_time')
                )      
            except Exception:
                pass
   
        #define queue number automaticly
        if self.cleaned_data.pop('is_printed',False):
            #get latest queue
            recent_queue = (
                models.Queue.objects
                .filter(service=new_queue.service)
                #.is_booking(self.cleaned_data.get('booking_flag', False))
                .today_filter()
                .is_printed(True)
                .order_by('print_datetime')
                .last()
            )
            new_queue.number= new_queue.number or (getattr(recent_queue, 'number', None) or 0)+1
            new_queue.print_datetime= new_queue.print_datetime or datetime.now()
        #save when commited
        if commit:
            new_queue.save()
        return new_queue
    
#todos finish this one
#then add one for booking
class AddQueueModelForms(QueueModelBaseForms):
    class Meta(QueueModelBaseForms.Meta):
        fields=('service','is_printed',)
class AddBookingQueuemodelForms(QueueModelBaseForms):
    class Meta(QueueModelBaseForms.Meta):
        fields = ('service','customer','is_booking')
class PrintBookingQueuemodelForms(QueueModelBaseForms):
    class Meta(QueueModelBaseForms.Meta):
        fields = ('is_printed',)
class CallQueueModelForms(QueueModelBaseForms):
    class Meta(QueueModelBaseForms.Meta):
        fields=('is_called','counter_booth',)
    def save(self, commit=True):
        new_queue = super(CallQueueModelForms,self).save(commit=False)
        new_queue.is_called = self.cleaned_data.pop('is_called',new_queue.is_called)
        if commit:
            new_queue.save()
        return new_queue        