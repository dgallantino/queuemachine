from django.contrib import admin
# Register your models here.
from queue_app import models, forms
from django.contrib.auth.admin import UserAdmin 

class QueueAdmin(admin.ModelAdmin):
    form = forms.QueueModelBaseForms
    model = models.Queue
    list_display = [ 'id', 'service','booking_flag','number',]
    list_filter = ('service','booking_flag', 'print_flag','call_flag')
    readonly_fields = (
                    'date_created',
                    'date_modified',
                    'character',
                    'number',
                    'booking_datetime',
                    'print_datetime',
                )
    fieldsets = (
        ('Front end fields', {
            'fields': (
                'service',
                'customer',
                ('booking_time','booking_date'),
                'counter_booth',
                'booking_flag',
                'call_flag',
                'print_flag',
            )
        }),
        ('Read only fields',{
            'classes':('collapse',),
            'fields':(
                'date_created',
                'date_modified',
                'character',
                'number',
                'booking_datetime',
                'print_datetime',
            ),
        }),
    )


#custom users
class CustomUserAdmin(UserAdmin):
    add_form = forms.CustomUserCreationForm
    form = forms.CustomUserChangeForm
    model = models.User
    list_display = [ 'username', 'first_name','last_name',]
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', ('first_name','last_name',),'password1', 'password2'),
        }),
    )
    fieldsets = UserAdmin.fieldsets + (
            ('Profile', {
                'fields': (
                    'organization','phone'
                )
            }
        ),
    )
    actions = ['set_selected_as_staff',]
    def set_selected_as_staff(self,request,query_set):
        query_set.update(is_staff = True)

admin.site.register(models.User, CustomUserAdmin)
admin.site.register(models.Service)
admin.site.register(models.Queue,QueueAdmin)
admin.site.register(models.Organization)
admin.site.register(models.CounterBooth)