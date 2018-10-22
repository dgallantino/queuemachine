'''
Created on Oct 1, 2018

@author: gallantino
'''
from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from queue_app import models, widgets
import datetime

class CustomUserCreationForm(UserCreationForm):
    
    class Meta(UserCreationForm.Meta):
        model = models.User
        fields ='__all__'
 
class CustomUserChangeForm(UserChangeForm):
 
    class Meta:
        model = models.User
        fields = ('username', 'email')

class QueueModelForms(forms.ModelForm):
    booking_time=forms.TimeField(
        required=False,
        widget=widgets.TimePicker(format='%H:%M',)
    )
    booking_date=forms.DateField(
        initial= datetime.datetime.now(),
        required=False,
        widget=widgets.DatePicker(format='%d %b %Y',)
    )

    class Meta:
        model=models.Queue
        fields='__all__'
        
    def save(self, commit=True):
        is_booking = self.cleaned_data.get('booking_flag', False)
    
        #get latest queue
        if is_booking:
            recent_queue = models.Queue.objects.get_booking().filter(service=self.cleaned_data.get('service')).last()
        else:
            recent_queue = models.Queue.objects.get_nonbooking().filter(service=self.cleaned_data.get('service')).last()
            
        #create new queue obj
        try:
            #get booking data
            self.cleaned_data['booking_datetime'] = datetime.datetime.combine(
                self.cleaned_data.pop('booking_date'),
                self.cleaned_data.pop('booking_time')
            )   
        except Exception:
            #when booking date and time not found
            self.cleaned_data['booking_datetime'] = None

        new_queue = super().save(commit=False)
        
        #define queue number automaticly
        if self.cleaned_data.pop('booking_flag'):
            new_queue.number = recent_queue.number+1 if recent_queue else 1 
            
        #save when commited
        if commit:
            new_queue.save()
        return new_queue