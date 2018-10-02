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