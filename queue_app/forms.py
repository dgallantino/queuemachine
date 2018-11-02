'''
Created on Oct 1, 2018

@author: gallantino
'''
from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from queue_app import models, widgets
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
        
        fields='__all__'
        
        widgets={
            'service':forms.Select(
                attrs={
                    'id':'service',
                    'class':'select-input',
                },
            ),
        }
    
    class Media:
        css={
            'all':('queue_app/core/css/add_booking_form.css',),
        }
        
    def save(self, commit=True):
        #get models.Queue isntance to create or update
        new_queue = super(QueueModelForms,self).save(commit=False)  
        
        #get latest queue
        recent_queue_queryset=models.Queue.objects.filter(service=self.cleaned_data.get('service')).printed()
        if self.cleaned_data.get('booking_flag', False):
            recent_queue = recent_queue_queryset.booking().last()
        else:
            recent_queue = recent_queue_queryset.nonbooking().last()
            
        #create new queue obj
        try:
            #get booking data
            if not self.cleaned_data.get('booking_datetime'):
                new_queue.booking_datetime = datetime.combine(
                    self.cleaned_data.pop('booking_date'),
                    self.cleaned_data.pop('booking_time')
                )                
        except Exception:
            #when booking date and time input not found
            new_queue.booking_datetime = None
                
        #define queue number automaticly
        if self.cleaned_data.pop('print_flag'):
            new_queue.number= (getattr(recent_queue, 'number', 0) or 0)+1
        
        #save when commited
        if commit:
            new_queue.save()
        return new_queue