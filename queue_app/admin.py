from django.contrib import admin
# Register your models here.
from queue_app.models import Service, Queue, User

from django.contrib.auth.admin import UserAdmin

from queue_app import forms


admin.site.register(Service)
admin.site.register(Queue)

#custom users
class CustomUserAdmin(UserAdmin):
    add_form = forms.CustomUserCreationForm
    form = forms.CustomUserChangeForm
    model = User
    list_display = ['email', 'username',]

admin.site.register(User, CustomUserAdmin)
