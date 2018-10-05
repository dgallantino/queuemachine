from django.urls import path
from queue_app import views
from django.conf import settings
from django.conf.urls.static import static

app_name='queue'
urlpatterns = [
    path('machine/',views.MachineDisplay.as_view(), name='machine_url'),
    path('machine/print-ticket/<uuid:pk>/', views.PrintTicket.as_view(), name='print_ticket_url'),
    path('manager/',views.ManagerDisplay.as_view(), name='manager_url'),
    path('manager/service/<uuid:pk>/', views.QueuePerService.as_view(), name='queue_per_service_url'),
    path('manager/queues/<uuid:pk>/', views.QueueRetriveUpdateAPI.as_view(), name='queue_retrive_update_url'),
]+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
