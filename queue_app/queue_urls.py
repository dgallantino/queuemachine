from django.urls import path
from queue_app import views
from django.conf import settings
from django.conf.urls.static import static

app_name='queue'
urlpatterns = [
    path(
        'signup/',                                 
        views.SignUp.as_view(), 
        name='sign_up'
    ),
    path(
        'machine/',                                
        views.MachineDisplay.as_view(), 
        name='machine_url'
    ),
    path(
        'machine/booking-list/',                   
        views.BookingList.as_view(), 
        name='booking_list_url'
    ),
    path(
        'machine/booking-list/<uuid:pk>/',         
        views.BookingListUpdate.as_view(), 
        name='booking_list_update_url'
    ),
    path(
        'machine/booking-list/<uuid:pk>/print/',   
        views.PrintBookingTicket.as_view(), 
        name='booking_print_url'
    ),
    path(
        'machine/print-ticket/<uuid:pk>/',         
        views.PrintTicket.as_view(), 
        name='print_ticket_url'
    ),
    path(
        'manager/',                                
        views.ManagerDisplay.as_view(), 
        name='manager_url'
    ),
    path(
        'manager/queues/service/<uuid:pk>/',       
        views.QueuePerService.as_view(), 
        name='queue_per_service_url'
    ),
    path(
        'manager/queues/add-booking/',             
        views.AddBookingQueueView.as_view(), 
        name='add_booking_url'
    ),
    path(
        'manager/users/',                          
        views.UserLookupView.as_view(),
        name='user_lookup_url'
    ),
    path(
        'manager/users/add/',                          
        views.AddCustomerView.as_view(),
        name='add_customer_url'
    ),
    path(
        'manager/services/',                       
        views.ServiceLookupView.as_view(),
        name='service_lookup_url'
    ),
]+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
