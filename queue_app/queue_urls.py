from django.urls import path
from queue_app import views
from django.conf import settings
from django.conf.urls.static import static

app_name='queue'
urlpatterns = [
    path('machine/',views.MachineDisplay.as_view(), name='machine_url'),
    path('machine/booking-list/',views.BookingList.as_view(), name='booking_list_url'),
    path('machine/booking-list/<uuid:pk>/',views.BookingListUpdate.as_view(), name='booking_list_update_url'),
    path('machine/print-ticket/<uuid:pk>/', views.PrintTicket.as_view(), name='print_ticket_url'),
    path('manager/',views.ManagerDisplay.as_view(), name='manager_url'),
    path('manager/queues/service/<uuid:pk>/', views.QueuePerService.as_view(), name='queue_per_service_url'),
    path('manager/queues/add-booking/', views.AddBookingQueue.as_view(), name='add_booking_url'),
]+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
