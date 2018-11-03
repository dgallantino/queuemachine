from django.contrib import admin
# Register your models here.
from queue_app import models
from django.contrib.auth.admin import UserAdmin

from queue_app import forms


admin.site.register(models.Service)
admin.site.register(models.Queue)
admin.site.register(models.Organization)


#custom users
class CustomUserAdmin(UserAdmin):
    add_form = forms.CustomUserCreationForm
    form = forms.CustomUserChangeForm
    model = models.User
    list_display = [ 'username', 'first_name','last_name',]
    fieldsets = UserAdmin.fieldsets + (
            (None, {'fields': ('organization',)}),
    )

admin.site.register(models.User, CustomUserAdmin)
