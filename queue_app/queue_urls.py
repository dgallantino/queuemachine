from django.urls import path
from queue_app import views
from django.conf import settings
from django.conf.urls.static import static

app_name='queue'
urlpatterns = [
    path(
        '',                                 
        views.IndexView.as_view(), 
        name='index_url'
    ),
    path(
        'signup/',                                 
        views.SignUp.as_view(), 
        name='sign_up'
    ),
    path(
        'machine/',                                
        views.MachineDisplayView.as_view(), 
        name='machine_url'
    ),
    path(
        'machine/booking-list/',                   
        views.BookingQueueListView.as_view(), 
        name='booking_list_url'
    ),
    path(
        'machine/booking-list/<uuid:pk>/',         
        views.BookingQueueListView.as_view(), 
        name='booking_list_update_url'
    ),
    path(
        'machine/booking-list/<uuid:pk>/print/',   
        views.PrintBookingTicketView.as_view(), 
        name='booking_print_url'
    ),
    path(
        'machine/print-ticket/<uuid:pk>/',         
        views.PrintTicketView.as_view(), 
        name='print_ticket_url'
    ),
    path(
        'manager/',                                
        views.ManagerDisplayView.as_view(), 
        name='manager_url'
    ),
    path(
        'manager/queues/add-booking/',             
        views.AddBookingQueueView.as_view(), 
        name='add_booking_url'
    ),
    path(
        'manager/queues/service/<uuid:pk>/',       
        views.QueuePerServiceView.as_view(), 
        name='queue_per_service_url'
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
    path(
        'manager/booths/',                       
        views.BoothListView.as_view(),
        name='booth_list_url'
    ),
    path(
        'manager/booths/<uuid:pk>/',                       
        views.BoothToSession.as_view(),
        name='booth_detail_url'
    ),
]+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
