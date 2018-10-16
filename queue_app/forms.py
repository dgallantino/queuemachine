'''
Created on Oct 1, 2018

@author: gallantino
'''
from django import forms
from queue_app import models

#repair booking_time field
#use splitDateTimeWidget
class QueueModelForms(forms.ModelForm):
    booking_time=forms.SplitDateTimeField();
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
        new_queue = models.Queue(**self.cleaned_data)

        if recent_queue:
            new_queue.number = recent_queue.number+1
        else :
            new_queue.number = 1
            
        #save when commited
        if commit:
            new_queue.save()
        return new_queue