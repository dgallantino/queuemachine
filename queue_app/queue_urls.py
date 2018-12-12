from django.urls import path
from queue_app import views
from django.conf import settings
from django.conf.urls.static import static


manager_patterns = [
    path(
        '',
        views.ManagerDisplayView.as_view(),
        name='index'
    ),
    path(
        'queues/<uuid:pk>/call/',
        views.CallQueueView.as_view(),
        name='call'
    ),
    path(
        'queues/add-booking/',
        views.AddBookingQueueView.as_view(),
        name='add_booking'
    ),
    path(
        'queues/service/<uuid:pk>/',
        views.QueuePerServiceView.as_view(),
        name='service_queues'
    ),
    path(
        'users/',
        views.UserLookupView.as_view(),
        name='user_autocomplete'
    ),
    path(
        'services/',
        views.ServiceLookupView.as_view(),
        name='service_autocomplete'
    ),
    path(
        'organization/lookup/',
        views.OrganizationLookupView.as_view(),
        name='organization_autocomplete'
    ),
    path(
        'customer/add/',
        views.AddCustomerView.as_view(),
        name='add_customer'
    ),
    path(
        'booths/',
        views.ManagerBoothListView.as_view(),
        name='booth_list'
    ),
    path(
        'booths/<uuid:pk>/',
        views.BoothToSession.as_view(),
        name='session_booth'
    ),
    path(
        'organization/',
        views.OrganizationListView.as_view(),
        name='organization_list'
    ),
    path(
        'organization/<uuid:pk>/',
        views.OrganizationToSession.as_view(),
        name='session_org'
    ),
    path(
        'queues/audiotest/',
        views.playAudioFile,
        name='audio'
    ),
]

machine_patterns =[
    path(
        '',
        views.MachineDisplayView.as_view(),
        name='index'
    ),
    path(
        'booking-list/',
        views.BookingQueueListView.as_view(),
        name='booking_list'
    ),
    path(
        'booking-list/<uuid:pk>/',
        views.BookingQueueListView.as_view(),
        name='booking_list_update'
    ),
    path(
        'print-ticket/<uuid:pk>/',
        views.PrintTicketView.as_view(),
        name='print'
    ),
]

board_patterns = [
    path(
        'infoboard/',
        views.InfoBoardMainView.as_view(),
        name='index'
    ),
    path(
        'infoboard/queues/',
        views.InfoBoardQueueListView.as_view(),
        name='queues'
    ),
    path(
        'infoboard/queues/service/<uuid:pk>/',
        views.InfoBoardQueuePerService.as_view(),
        name='service_queues'
    ),
    path(
        'infoboard/booths/<uuid:pk>/details/',
        views.InfoBoardBoothDetailView.as_view(),
        name='booth_detail'
    ),
]

urlpatterns = [
    path('manager/', include(manager_patterns,namaspace='manager'))
    path('machine/', include(machine_patterns,namespace='machine'))
    path('infoboard/', include(board_patterns,namaspace='infoboard'))
    path(
        '',
        views.IndexView.as_view(),
        name='index'
    ),
    path(
        'signup/',
        views.SignUp.as_view(),
        name='sign_up'
    ),
]+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
