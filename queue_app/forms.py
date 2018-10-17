'''
Created on Oct 1, 2018

@author: gallantino
'''
from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from queue_app import models
import datetime

class CustomUserCreationForm(UserCreationForm):
     
    class Meta(UserCreationForm.Meta):
        model = models.User
        fields ='__all__'
 
class CustomUserChangeForm(UserChangeForm):
 
    class Meta:
        model = models.User
        fields = ('username', 'email')

#repair booking_time field
#use splitDateTimeWidget
class QueueModelForms(forms.ModelForm):
    booking_time=forms.TimeField(initial= datetime.datetime.now())
    booking_date=forms.DateField(initial= datetime.datetime.now())

    def __init__(self, *args, **kwargs):
        super(QueueModelForms, self).__init__(*args, **kwargs)
        # Making customer required
        self.fields['customer'].required = True

    class Meta:
        model=models.Queue
        fields='__all__'
        widgets={
            'booking_time':forms.TimeInput(
                attrs={
                    'class':'time_field',
                }
            ),
            'booking_date':forms.DateInput(
                attrs={
                    'class':'date_field',
                }
            )
        }
        
    def save(self, commit=True):
        is_booking = self.cleaned_data.get('booking_flag', False)
    
        #get latest queue
        if is_booking:
            recent_queue = models.Queue.objects.get_booking().filter(service=self.cleaned_data.get('service')).last()
        else:
            recent_queue = models.Queue.objects.get_nonbooking().filter(service=self.cleaned_data.get('service')).last()
            
        #create new queue obj
        self.cleaned_data['booking_datetime'] = datetime.datetime.combine(
            self.cleaned_data.pop('booking_date'),
            self.cleaned_data.pop('booking_time')
        )
        new_queue = models.Queue(**self.cleaned_data)
        
        #define queue number automaticly
        if recent_queue:
            new_queue.number = recent_queue.number+1
        else :
            new_queue.number = 1
            
        #save when commited
        if commit:
            new_queue.save()
        return new_queue