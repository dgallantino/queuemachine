'''
Created on Oct 1, 2018

@author: gallantino
'''
from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from queue_app import models, widgets
from dal import autocomplete
from datetime import datetime
class CustomUserCreationForm(UserCreationForm):
    
    class Meta(UserCreationForm.Meta):
        model = models.User
        fields ='__all__'
 
class CustomUserChangeForm(UserChangeForm):
 
    class Meta:
        model = models.User
        fields = '__all__'
        

class QueueModelForms(forms.ModelForm):
    
    booking_time=forms.TimeField(
        label="Booking Time",
        initial= datetime.now(),
        required=False,
        widget=widgets.TimePicker(
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
        widget=widgets.DatePicker(
            format='%d-%m-%Y',
            attrs={
                'id':'booking-date',
                'class':'input-field',
            },
        ),
    )

    class Meta:
        model=models.Queue
        
        exclude = [
            'booking_datetime',
            'print_datetime',
            'character',
            'number',
        ]
        
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
            'all':('queue_app/core/css/add_booking_form.css',),
        }
        
    
    def save(self, commit=True):
        #get models.Queue isntance to create or edit
        new_queue = super(QueueModelForms,self).save(commit=False)  
        
        try:
        #get booking data
            new_queue.booking_datetime = datetime.combine(
                self.cleaned_data.pop('booking_date'),
                self.cleaned_data.pop('booking_time')
            )      
        except Exception:
            pass
   
        #define queue number automaticly
        if self.cleaned_data.pop('print_flag'):
            #get latest queue
            recent_queue = (
                models.Queue.objects.filter(service=self.cleaned_data.get('service'))
                #.is_booking(self.cleaned_data.get('booking_flag', False))
                .is_printed(True)
                .order_by('print_datetime')
                .last()
            )
            new_queue.number= (getattr(recent_queue, 'number', None) or 0)+1
            new_queue.print_datetime=datetime.now()
        #save when commited
        if commit:
            new_queue.save()
        return new_queue