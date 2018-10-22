from django import forms

class DatePicker(forms.DateInput):
    class Media:
        css={
            'all':('queue_app/jquery-ui/jquery-ui.min.css',),
        }
        js=('queue_app/jquery-ui/jquery-ui.min.js',)
        
class TimePicker(forms.TimeInput):
    class Media:
        css={
            'all':('queue_app/jquery-timepicker/jquery.timepicker.min.css',),
        }
        js=('queue_app/jquery-timepicker/jquery.timepicker.min.js',)