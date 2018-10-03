'''
Created on Oct 1, 2018

@author: gallantino
'''
from django import forms
from queue_app import models


class QueueModelForms(forms.ModelForm):
    class Meta:
        model=models.Queue
        fields='__all__'
    def save(self, commit=True):
        recent_queue = models.Queue.objects.get_today_list().filter(service=self.cleaned_data.get('service')).last()
        if recent_queue:
            new_queue = models.Queue(
                number=recent_queue.number+1,
                service=self.cleaned_data.get('service')
            )
        else :
            new_queue = models.Queue(
                number=1,
                service=self.cleaned_data.pop('service')
            )
        if commit:
            new_queue.save()
        return new_queue