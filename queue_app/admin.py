from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group
from django.utils.translation import gettext as _


# Register your models here.
from queue_app import models, forms

admin.site.unregister(Group)

class QueueAdmin(admin.ModelAdmin):
    form = forms.QueueModelBaseForms
    model = models.Queue
    list_display = [ 'id', 'service','number','is_booking','is_called',]
    list_filter = ('service','is_booking', 'is_printed','is_called')
    date_hierarchy = 'date_created'
    readonly_fields = (
                    'date_created',
                    'date_modified',
                    'character',
                    'number',
                    'booking_datetime',
                    'print_datetime',
                )
    fieldsets = (
        (_('Editable'), {
            'fields': (
                'service',
                'customer',
                ('booking_time','booking_date'),
                'counter_booth',
                'is_booking',
                'is_called',
                'is_printed',
            )
        }),
        (_('Read onlies'),{
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
    list_display = ('username', 'first_name','last_name',)
    list_filter = UserAdmin.list_filter+('organization',)
    filter_horizontal = UserAdmin.filter_horizontal + ('organization',)
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', ('first_name','last_name',),'password1', 'password2'),
        }),
    )
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': (('first_name', 'last_name',),
                                        'email', 'phone',)}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
                                       'organization','groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    actions = ['set_selected_as_staff',]
    def set_selected_as_staff(self,request,query_set):
        query_set.update(is_staff = True)

class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'organization',)
    list_filter = ('organization',)

admin.site.register(models.User, CustomUserAdmin)
admin.site.register(models.Service, ServiceAdmin)
admin.site.register(models.Queue,QueueAdmin)
admin.site.register(models.Organization)
admin.site.register(models.CounterBooth)
